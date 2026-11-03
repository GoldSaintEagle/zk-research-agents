#!/usr/bin/env python3
"""verify_bib.py -- check every BibTeX entry against IACR ePrint / Crossref / DBLP,
and @misc URL sources (blogs, HackMD, project docs, audit reports) against the live
URL + the Wayback Machine.

Why: fabricated or garbled references (invented co-authors, placeholder
"Chen and others", wrong venue, a key pointing at a different paper) are a
research-integrity problem and an instant credibility loss with reviewers.
LLM-drafted bibliographies are especially prone to this.  This script is the
mechanical half of the `bib-verify` gate; the human/agent half is reading the
flagged entries.

Usage
-----
    python3 verify_bib.py refs.bib                       # Markdown report on stdout
    python3 verify_bib.py refs.bib --json report.json    # + machine-readable report
    python3 verify_bib.py refs.bib --offline             # static lint only
    python3 verify_bib.py refs.bib --only key1,key2      # re-check a few entries
    python3 verify_bib.py refs.bib --url-timeout 5       # per-request timeout for URL sources
    python3 verify_bib.py --selftest

Resolution order per entry
--------------------------
1. ePrint id (from `eprint=`, `url=`, `howpublished=`, `note=`, `journal=` text
   such as "Cryptology ePrint Archive, Paper 2019/953")  ->  ePrint OAI-PMH record.
   If eprint.iacr.org is not usable from this client (refused, redirected to the IACR block
   notice, no answer; see eprint-search/scripts/eprint_source.py) the rest of the run skips
   it: an entry with a `doi=` is then checked through the DOI (step 2), and only an entry
   without one is looked up on the third-party mirror (https://eprint.iacr.asia, JSON
   search API, then its OAI-PMH) -> status `VERIFIED (mirror)` if it matches.
2. `doi=`  ->  Crossref /works/<doi>, falling back to DataCite (Zenodo, LIPIcs, arXiv DOIs).
   Crossref's separate `subtitle` field is joined to the title ("Title: Subtitle") before
   comparing; the main title alone is compared too, and the better score counts.
3. `@misc`/`@online` with a URL and neither ePrint id nor DOI (gray literature)  ->
   URL check: (a) the URL answers (HEAD, GET fallback, with timeout); (b) a Wayback
   snapshot exists (an explicit web.archive.org link in `archiveurl=`/`note=`/
   `howpublished=`, else the archive.org availability API); (c) an access date is
   recorded (`urldate = {YYYY-MM-DD}` or "Accessed YYYY-MM-DD" in `note=`).
4. otherwise title search: DBLP (if reachable) then Crossref bibliographic query.
5. a `@book` with a `url` and neither ePrint id nor DOI that the title search does not
   find (NOT_FOUND; e.g. an open book published from a repository) -> the URL check of
   step 3. The detail says that the title search failed, so the result reads as "the
   URL source exists and is archived", not as "a publisher record was found".

Each entry gets a status:
  VERIFIED     title similarity >= 0.90 and >= 1 author surname overlap (and year +-1 if given)
  VERIFIED (mirror)  the same test, passed against the third-party ePrint mirror's record
               (official site unusable, no DOI on the entry); passes the gate, reported apart
  MISMATCH     a record was found for the id/DOI but title or authors disagree
  WEAK         best title-search hit is similar but not conclusive (0.75..0.90) -> check by hand
  NOT_FOUND    nothing plausible found -> treat as fabricated until proven otherwise
  NEEDS_VERIFICATION  URL source failing (a), (b) or (c) above -> not proof of fabrication,
               but it cannot be cited until fixed or checked by hand
  UNCHECKED    offline / service error
plus static LINT flags (placeholder authors, "and others" only, missing year/title,
`% UNVERIFIED` marker in the .bib, duplicate titles, ...).

Exit status: 0 if every entry is VERIFIED or VERIFIED (mirror) (lint warnings allowed;
--require-official makes mirror rows fail), 1 if any entry is MISMATCH/NOT_FOUND/WEAK/
NEEDS_VERIFICATION/UNCHECKED, 3 on usage errors.  Use it as a gate.

Network: every request (ePrint, mirror, Crossref, DataCite, DBLP, Wayback, URL probes) goes
through eprint-search/scripts/polite_http.py: >= 3 s between two requests to one host,
Retry-After and backoff on 429/503, a 7-day cache in .cache/eprint/, and at most 300
requests per run (--max-requests); when the cap is reached the run stops, the remaining
entries are UNCHECKED, and a re-run continues from the cache.
"""
from __future__ import annotations

import argparse
import difflib
import html
import json
import os
import re
import sys
import unicodedata
import urllib.error
import urllib.parse

# shared rate limiter + ePrint access (official, then mirror); install.sh copies both skills
_EPRINT_SCRIPTS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "eprint-search", "scripts")
sys.path.insert(0, os.path.normpath(_EPRINT_SCRIPTS))
import polite_http  # noqa: E402
from eprint_source import EprintSource, EprintUnavailable  # noqa: E402

UA = polite_http.UA
VERIFIED_STATUSES = ("VERIFIED", "VERIFIED (mirror)")
MIRROR_URL_RE = re.compile(r"eprint\.iacr\.asia", re.I)
CROSSREF = "https://api.crossref.org/works"
DATACITE = "https://api.datacite.org/dois"
DBLP = "https://dblp.org/search/publ/api"
WAYBACK_API = "https://archive.org/wayback/available?url={url}"
URL_TYPES = ("misc", "online", "electronic", "www")
ARCHIVE_RE = re.compile(r"https?://(?:web\.)?archive\.org/web/\S+?(?=[\s}]|$)", re.I)
ACCESSED_RE = re.compile(r"\baccessed(?:\s+on)?:?\s*(\d{4}-\d{2}-\d{2})\b", re.I)
EPRINT_ID = re.compile(r"(?:eprint\.iacr\.org/|ePrint Archive,?\s*(?:Paper|Report)?\s*|^)"
                       r"((?:19|20)\d{2})/(\d{1,5})\b", re.I)


# ------------------------------------------------------------- bib parsing ---

def parse_bib(text: str) -> list[dict]:
    """Small dependency-free BibTeX parser (handles nested braces and quotes).

    Returns dicts with keys: type, key, fields (lower-cased names), unverified_marker.
    A line `% UNVERIFIED` directly above an entry sets unverified_marker=True.
    """
    entries = []
    i, n = 0, len(text)
    while True:
        at = text.find("@", i)
        if at < 0:
            break
        m = re.match(r"@(\w+)\s*([{(])", text[at:])
        if not m:
            i = at + 1
            continue
        etype = m.group(1).lower()
        if etype in ("comment", "preamble", "string"):
            i = at + m.end()
            continue
        preceding = text[text.rfind("\n", 0, max(0, text.rfind("\n", 0, at))) + 1:at]
        marker = "UNVERIFIED" in preceding.upper()
        j = at + m.end()
        depth, k = 1, j
        while k < n and depth:
            c = text[k]
            if c in "{(":
                depth += 1
            elif c in "})":
                depth -= 1
            k += 1
        body = text[j:k - 1]
        key, _, rest = body.partition(",")
        fields = {}
        p = 0
        while p < len(rest):
            fm = re.match(r"\s*([\w\-:]+)\s*=\s*", rest[p:])
            if not fm:
                break
            name = fm.group(1).lower()
            p += fm.end()
            if p < len(rest) and rest[p] == "{":
                d, q = 1, p + 1
                while q < len(rest) and d:
                    d += {"{": 1, "}": -1}.get(rest[q], 0)
                    q += 1
                val = rest[p + 1:q - 1]
                p = q
            elif p < len(rest) and rest[p] == '"':
                q = p + 1
                while q < len(rest) and not (rest[q] == '"' and rest[q - 1] != "\\"):
                    q += 1
                val = rest[p + 1:q]
                p = q + 1
            else:
                vm = re.match(r"[^,]*", rest[p:])
                val = vm.group(0).strip()
                p += vm.end()
            fields[name] = re.sub(r"\s+", " ", val).strip()
            cm = re.match(r"\s*,", rest[p:])
            if cm:
                p += cm.end()
        entries.append({"type": etype, "key": key.strip(), "fields": fields,
                        "unverified_marker": marker})
        i = k
    return entries


# ----------------------------------------------------------- normalisation ---

_LATEX_ACCENT = re.compile(r"\\[`'^\"~=.uvHtcdbk]\s*\{?\s*([A-Za-z])\s*\}?")


def delatex(s: str) -> str:
    s = _LATEX_ACCENT.sub(r"\1", s or "")
    s = re.sub(r"\\(ss|o|O|l|L|aa|AA|ae|AE)\b", lambda m: {"ss": "ss", "o": "o", "O": "O", "l": "l",
                                                        "L": "L", "aa": "a", "AA": "A",
                                                        "ae": "ae", "AE": "AE"}[m.group(1)], s)
    s = re.sub(r"\$[^$]*\$", " ", s)            # math in titles
    s = re.sub(r"\\[a-zA-Z]+", " ", s)
    s = s.replace("{", "").replace("}", "").replace("~", " ")
    s = unicodedata.normalize("NFKD", html.unescape(s))
    return "".join(c for c in s if not unicodedata.combining(c))


def norm_title(s: str) -> str:
    s = delatex(s).lower()
    s = re.sub(r"[^a-z0-9 ]+", " ", s)
    return re.sub(r"\s+", " ", s).strip()


def title_sim(a: str, b: str) -> float:
    a, b = norm_title(a), norm_title(b)
    if not a or not b:
        return 0.0
    if a == b:
        return 1.0
    # tolerate a subtitle present on one side only
    if a.startswith(b) or b.startswith(a):
        short = min(len(a), len(b))
        if short >= 25:
            return 0.93
    return difflib.SequenceMatcher(None, a, b).ratio()


def surnames_from_bib(author_field: str) -> list[str]:
    out = []
    for a in re.split(r"\s+and\s+", delatex(author_field or "")):
        a = a.strip()
        if not a or a.lower() in ("others", "et al", "et al."):
            continue
        last = a.split(",")[0] if "," in a else a.split()[-1]
        out.append(norm_title(last).replace(" ", ""))
    return [x for x in out if x]


def surname_of(full: str) -> str:
    full = delatex(full).strip()
    if "," in full:
        return norm_title(full.split(",")[0]).replace(" ", "")
    return norm_title(full.split()[-1] if full.split() else "").replace(" ", "")


# ---------------------------------------------------------------- services ---

class Blocked(OSError):
    pass


def client() -> polite_http.PoliteClient:
    return polite_http.default_client()


def http_get(url: str, timeout: float | None = None) -> str:
    """Body of a 2xx answer through the shared polite client (redirects followed)."""
    return client().get_text(url)


def url_reachable(url: str, timeout: float = 10.0) -> tuple[bool, str]:
    """HEAD, then GET for servers that refuse HEAD; a redirect counts as an answer.
    Rate-limited like every other request.  Never raises (except RequestBudgetExceeded)."""
    c, last = client(), ""
    saved, c.timeout = c.timeout, timeout
    try:
        for method in ("HEAD", "GET"):
            try:
                r = c.request(url, method=method, cache=False)
            except polite_http.HTTPStatusError as e:
                return False, f"{method} HTTP {e.status}"
            except (urllib.error.URLError, TimeoutError, OSError, ValueError) as e:
                return False, f"{method} {e}"
            if r.status < 400:
                return True, f"{method} {r.status}"
            last = f"{method} HTTP {r.status}"
            if r.status not in (403, 405, 501):
                return False, last
        return False, last
    finally:
        c.timeout = saved


def wayback_snapshot(url: str, timeout: float = 10.0) -> str | None:
    """Closest Wayback snapshot URL, or None.  Raises on service errors."""
    data = json.loads(http_get(WAYBACK_API.format(url=urllib.parse.quote(url, safe="")), timeout=timeout))
    snap = (data.get("archived_snapshots") or {}).get("closest") or {}
    return snap.get("url") if snap.get("available") else None


def eprint_source(state: dict) -> EprintSource:
    """One EprintSource per run (it remembers that the official site is down)."""
    if "eprint_source" not in state:
        state["eprint_source"] = EprintSource(client(), allow_mirror=not state.get("no_mirror"))
    return state["eprint_source"]


def fetch_crossref_doi(doi: str) -> dict | None:
    """Crossref first; DataCite for DOIs Crossref does not know (Zenodo, LIPIcs, arXiv...)."""
    try:
        data = json.loads(http_get(f"{CROSSREF}/{urllib.parse.quote(doi)}"))
        return _crossref_item(data.get("message", {}))
    except polite_http.HTTPStatusError as e:
        if e.status != 404:
            raise
    try:
        data = json.loads(http_get(f"{DATACITE}/{urllib.parse.quote(doi)}"))
    except polite_http.HTTPStatusError as e:
        if e.status == 404:
            return None
        raise
    return _datacite_item(data, doi)


def _datacite_item(data: dict, doi: str) -> dict:
    at = data.get("data", {}).get("attributes", {})
    names = []
    for c in at.get("creators", []):
        if c.get("givenName") or c.get("familyName"):
            names.append(f"{c.get('givenName', '')} {c.get('familyName', '')}".strip())
        else:
            nm = c.get("name", "")
            names.append(" ".join(reversed(nm.split(", "))) if ", " in nm else nm)
    titles = at.get("titles", [])
    main = " ".join(t.get("title", "") for t in titles if not t.get("titleType"))[:1000] or \
        " ".join(t.get("title", "") for t in titles[:1])
    subs = [t.get("title", "") for t in titles if t.get("titleType") == "Subtitle"]
    return {"title": join_subtitle(main, subs), "alt_titles": [main] if subs else [],
            "authors": names, "year": at.get("publicationYear"),
            "venue": at.get("publisher", ""), "source": f"DataCite doi:{doi}"}


def join_subtitle(title: str, subtitles: list[str]) -> str:
    """'Delegating Computation' + ['Interactive Proofs for Muggles'] -> 'Delegating Computation:
    Interactive Proofs for Muggles' (Crossref and DataCite keep subtitles in a separate field)."""
    title = re.sub(r"\s+", " ", title or "").strip()
    for sub in subtitles or []:
        sub = re.sub(r"\s+", " ", sub or "").strip()
        if sub and norm_title(sub) not in norm_title(title):
            title = f"{title}: {sub}" if title else sub
    return title


def _crossref_item(it: dict) -> dict:
    year = None
    for k in ("published-print", "published-online", "issued"):
        dp = (it.get(k) or {}).get("date-parts")
        if dp and dp[0] and dp[0][0]:
            year = dp[0][0]
            break
    main = " ".join(it.get("title") or [])
    subs = it.get("subtitle") or []
    return {"title": join_subtitle(main, subs), "alt_titles": [main] if subs else [],
            "authors": [f"{a.get('given', '')} {a.get('family', '')}".strip() for a in it.get("author", [])],
            "year": year, "venue": " ".join(it.get("container-title") or []),
            "source": f"Crossref doi:{it.get('DOI', '')}"}


def search_crossref(title: str, author_hint: str) -> list[dict]:
    q = {"query.bibliographic": title, "rows": 5,
         "select": "title,subtitle,author,DOI,issued,published-print,published-online,container-title"}
    if author_hint:
        q["query.author"] = author_hint
    data = json.loads(http_get(f"{CROSSREF}?{urllib.parse.urlencode(q)}"))
    return [_crossref_item(it) for it in data.get("message", {}).get("items", [])]


def search_dblp(title: str) -> list[dict]:
    raw = http_get(f"{DBLP}?{urllib.parse.urlencode({'q': title, 'format': 'json', 'h': 5})}")
    if raw.lstrip().startswith("<"):
        raise Blocked("DBLP bot challenge")
    out = []
    for h in json.loads(raw).get("result", {}).get("hits", {}).get("hit") or []:
        info = h.get("info", {})
        au = info.get("authors", {}).get("author", [])
        au = au if isinstance(au, list) else [au]
        out.append({"title": html.unescape(info.get("title", "")).rstrip("."),
                    "authors": [re.sub(r"\s+\d{4}$", "", a.get("text", "") if isinstance(a, dict) else str(a))
                                for a in au],
                    "year": int(info.get("year", 0) or 0) or None,
                    "venue": info.get("venue", "") if isinstance(info.get("venue"), str) else "",
                    "source": f"DBLP {info.get('key', '')}"})
    return out


# ---------------------------------------------------------------- checking ---

def entry_url(f: dict) -> str | None:
    if f.get("url"):
        return re.sub(r"^\\url\{(.*)\}$", r"\1", f["url"].strip())
    for k in ("howpublished", "note"):
        m = re.search(r"\\url\{([^}]+)\}", f.get(k, ""))
        if m and not ARCHIVE_RE.match(m.group(1)):
            return m.group(1)
    return None


def access_date(f: dict) -> str | None:
    if re.fullmatch(r"\d{4}-\d{2}-\d{2}", f.get("urldate", "").strip()):
        return f["urldate"].strip()
    for k in ("note", "howpublished", "addendum"):
        m = ACCESSED_RE.search(f.get(k, ""))
        if m:
            return m.group(1)
    return None


def explicit_archive(f: dict) -> str | None:
    for k in ("archiveurl", "archive", "note", "howpublished", "addendum"):
        m = ARCHIVE_RE.search(f.get(k, ""))
        if m:
            return m.group(0)
    return None


def is_url_source(e: dict) -> bool:
    """Gray literature: @misc/@online with a URL and no ePrint id / DOI to resolve."""
    f = e["fields"]
    return e["type"] in URL_TYPES and bool(entry_url(f)) and not find_eprint_id(f) and not f.get("doi")


def is_url_book(e: dict) -> bool:
    """A @book that can only be resolved through its URL: url given, no ePrint id, no DOI."""
    f = e["fields"]
    return e["type"] == "book" and bool(entry_url(f)) and not find_eprint_id(f) and not f.get("doi")


def check_url_source(e: dict, state: dict) -> tuple[str, str]:
    """Return (status, detail).  Network calls go through state['probe'] / state['wayback']
    so the selftest can inject fakes; every real call has a timeout."""
    f = e["fields"]
    url, tmo = entry_url(f), state.get("url_timeout", 10.0)
    probe = state.get("probe", url_reachable)
    wayback = state.get("wayback", wayback_snapshot)
    problems, notes = [], []
    ok, how = probe(url, tmo)
    (notes if ok else problems).append(f"URL {'reachable' if ok else 'unreachable'} ({how})")
    snap = explicit_archive(f)
    if not snap:
        try:
            snap = wayback(url, tmo)
        except (urllib.error.URLError, TimeoutError, OSError, ValueError) as exc:
            problems.append(f"Wayback lookup failed: {exc}")
            snap = ""
        if snap is None:
            problems.append("no Wayback snapshot (archive it and add archiveurl=)")
    if snap:
        notes.append(f"snapshot {snap[:80]}")
    acc = access_date(f)
    if acc:
        notes.append(f"accessed {acc}")
    else:
        problems.append("no access date (add urldate = {YYYY-MM-DD})")
    detail = f"{url[:80]}: " + "; ".join(problems + notes)
    return ("NEEDS_VERIFICATION" if problems else "VERIFIED"), detail


def find_eprint_id(f: dict) -> str | None:
    for k in ("eprint", "url", "howpublished", "note", "journal", "booktitle", "publisher"):
        v = f.get(k, "")
        m = EPRINT_ID.search(v) if k != "eprint" else re.search(r"((?:19|20)\d{2})/(\d{1,5})", v)
        if m:
            return f"{m.group(1)}/{int(m.group(2)):03d}"
    return None


def lint(e: dict) -> list[str]:
    f, flags = e["fields"], []
    au = f.get("author", "")
    if not f.get("title"):
        flags.append("missing title")
    if not au and e["type"] not in ("misc", "book", "manual", "online"):
        flags.append("missing author")
    if re.fullmatch(r"\s*\{?\s*\w+\s+and\s+others\s*\}?\s*", au or ""):
        flags.append("placeholder author list ('X and others' only)")
    if re.search(r"\b(anonymous|author\d|firstname|lastname|tbd|todo|xxx)\b", au, re.I):
        flags.append("placeholder author name")
    if not f.get("year") and not f.get("date"):
        flags.append("missing year")
    if re.search(r"\b(tbd|todo|xxx|\?\?)\b", " ".join(f.values()), re.I):
        flags.append("TODO/TBD text in entry")
    if e["unverified_marker"]:
        flags.append("marked % UNVERIFIED in source")
    if (is_url_source(e) or is_url_book(e)) and not access_date(f):
        flags.append("URL source without access date (urldate)")
    if any(MIRROR_URL_RE.search(f.get(k, "")) for k in ("url", "howpublished", "note")):
        flags.append("ePrint mirror URL in entry: cite the official https://eprint.iacr.org/YYYY/NNNN")
    return flags


def judge(entry: dict, rec: dict | None, how: str) -> tuple[str, float, str]:
    f = entry["fields"]
    if rec is None:
        return "NOT_FOUND", 0.0, f"no record via {how}"
    ts = max(title_sim(f.get("title", ""), t) for t in [rec["title"]] + list(rec.get("alt_titles") or []))
    bib_s = set(surnames_from_bib(f.get("author", "")))
    rec_s = {surname_of(a) for a in rec["authors"]}
    overlap = len(bib_s & rec_s)
    missing = sorted(bib_s - rec_s)
    year_ok = True
    if f.get("year", "").strip()[:4].isdigit() and rec.get("year"):
        y = int(f["year"].strip()[:4])
        years = {rec["year"], rec.get("last_year") or rec["year"]}
        year_ok = any(abs(y - yy) <= 1 for yy in years if yy)
    detail = (f"{rec['source']}: \"{rec['title'][:80]}\"; title_sim={ts:.2f}; "
              f"author overlap {overlap}/{len(bib_s) or '?'}")
    if missing and bib_s:
        detail += f"; bib surnames not in record: {', '.join(missing)}"
    if not year_ok:
        detail += f"; year {f.get('year')} vs {rec.get('year')}"
    if ts >= 0.90 and (overlap >= 1 or not bib_s) and not missing and year_ok:
        return "VERIFIED", ts, detail
    if ts >= 0.90 and overlap >= 1 and year_ok and len(missing) <= max(0, len(bib_s) // 4):
        return "VERIFIED", ts, detail + " (minor author-name variance)"
    if how.startswith("id"):
        return "MISMATCH", ts, detail
    if ts >= 0.75:
        return "WEAK", ts, detail
    return "NOT_FOUND", ts, detail


def check_entry(e: dict, offline: bool, state: dict) -> dict:
    f = e["fields"]
    res = {"key": e["key"], "type": e["type"], "title": delatex(f.get("title", ""))[:120],
           "lint": lint(e), "status": "UNCHECKED", "score": 0.0, "detail": ""}
    if offline:
        res["detail"] = "offline mode"
        return res
    if is_url_source(e):
        res["status"], res["detail"] = check_url_source(e, state)
        res["score"] = 1.0 if res["status"] == "VERIFIED" else 0.0
        return res
    try:
        eid = find_eprint_id(f)
        doi = re.sub(r"^https?://(dx\.)?doi\.org/", "", f.get("doi", "").strip())
        fetch_doi = state.get("fetch_doi", fetch_crossref_doi)
        if eid:
            src = eprint_source(state)
            got, rec = src.official_record(eid)
            if got != "down":
                res["status"], res["score"], res["detail"] = judge(e, rec, f"id ePrint {eid}")
                if res["status"] == "VERIFIED" or not doi:
                    return res
            else:
                # official site unusable: a DOI (publisher record) is preferred over the mirror
                note = f"official ePrint unusable ({src.official_down})"
                if doi:
                    res["status"], res["score"], res["detail"] = judge(e, fetch_doi(doi), f"id doi {doi}")
                    res["detail"] = f"{note}; checked via DOI: " + res["detail"]
                    if res["status"] == "VERIFIED" or not src.allow_mirror:
                        return res
                if not src.allow_mirror:
                    res["status"], res["detail"] = "UNCHECKED", f"ePrint {eid} not checked: {note}; mirror disabled"
                    return res
                via_doi = res["detail"] if doi else ""
                src.used_mirror = True
                st, sc, det = judge(e, src.mirror_record(eid, delatex(f.get("title", ""))), f"id ePrint {eid}")
                if st == "VERIFIED":
                    res["status"], res["score"], res["detail"] = "VERIFIED (mirror)", sc, det
                elif not doi:
                    res["status"], res["score"], res["detail"] = st, sc, det
                else:
                    res["detail"] = via_doi + f"; mirror: {st} ({det})"
                return res
        if doi:
            res["status"], res["score"], res["detail"] = judge(e, fetch_doi(doi), f"id doi {doi}")
            return res
        title = delatex(f.get("title", ""))
        if not title:
            res["status"], res["detail"] = "NOT_FOUND", "no title, no id"
            return res
        cands, used = [], []
        if not state.get("dblp_blocked"):
            try:
                cands += state.get("search_dblp", search_dblp)(title)
                used.append("DBLP")
            except (Blocked, ValueError):
                state["dblp_blocked"] = True
        first = (surnames_from_bib(f.get("author", "")) or [""])[0]
        cands += state.get("search_crossref", search_crossref)(title, first)
        used.append("Crossref")
        best = max(cands, key=lambda r: title_sim(title, r["title"]), default=None)
        res["status"], res["score"], res["detail"] = judge(e, best, "search " + "+".join(used))
        if res["status"] == "NOT_FOUND" and is_url_book(e):
            searched = res["detail"]
            res["status"], res["detail"] = check_url_source(e, state)
            res["score"] = 1.0 if res["status"] == "VERIFIED" else 0.0
            res["detail"] = f"@book via URL (title search: {searched}); " + res["detail"]
    except (urllib.error.URLError, TimeoutError, OSError, ValueError) as exc:   # incl. EprintUnavailable
        res["status"], res["detail"] = "UNCHECKED", f"service error: {exc}"
    return res


def duplicate_titles(entries: list[dict]) -> dict[str, list[str]]:
    seen: dict[str, list[str]] = {}
    for e in entries:
        t = norm_title(e["fields"].get("title", ""))
        if t:
            seen.setdefault(t, []).append(e["key"])
    return {t: ks for t, ks in seen.items() if len(ks) > 1}


def render(results: list[dict], dups: dict) -> str:
    order = {"MISMATCH": 0, "NOT_FOUND": 1, "WEAK": 2, "NEEDS_VERIFICATION": 3, "UNCHECKED": 4,
             "VERIFIED (mirror)": 5, "VERIFIED": 6}
    counts: dict[str, int] = {}
    for r in results:
        counts[r["status"]] = counts.get(r["status"], 0) + 1
    lines = ["# bib-verify report", "",
             "Summary: " + ", ".join(f"{k}={v}" for k, v in sorted(counts.items(), key=lambda kv: order[kv[0]])),
             "", "| status | key | score | lint | detail |", "|---|---|---|---|---|"]
    for r in sorted(results, key=lambda r: (order[r["status"]], r["key"])):
        lines.append(f"| {r['status']} | `{r['key']}` | {r['score']:.2f} | {'; '.join(r['lint'])} | "
                     f"{r['detail'].replace('|', '/')} |")
    if dups:
        lines += ["", "## Duplicate titles", ""] + [f"- {', '.join(ks)}" for ks in dups.values()]
    return "\n".join(lines) + "\n"


# ---------------------------------------------------------------- selftest ---

SELFTEST_BIB = r"""
@misc{GWC19,
  author = {Ariel Gabizon and Zachary J. Williamson and Oana Ciobotaru},
  title = {{PLONK}: Permutations over Lagrange-bases for Oecumenical Noninteractive arguments of Knowledge},
  howpublished = {Cryptology ePrint Archive, Paper 2019/953},
  year = 2019,
}
% UNVERIFIED
@article{fake,
  author = "Chen and others",
  title = {A Paper That Does Not Exist About Quantum Fuzzy Toys},
  journal = {IEEE TIFS}, year = {2024}
}
"""

# Synthetic gray-literature entries; example.org hosts, no real posts.
SELFTEST_URL_BIB = r"""
@misc{blog-ok,
  author = {Toy Author}, title = {A Toy Note on Sum-Check Batching},
  howpublished = {\url{https://blog.example.org/toy-sumcheck}},
  urldate = {2026-01-15}, year = {2026},
}
@misc{blog-nodate,
  title = {Toy Lookup Argument Notes},
  url = {https://hackmd.example.org/toy-lookup}, year = {2025},
  note = {Archived at \url{https://web.archive.org/web/20250101000000/https://hackmd.example.org/toy-lookup}},
}
@online{blog-dead,
  title = {Toy Folding Post}, url = {https://dead.example.org/toy-folding},
  urldate = {2026-02-01}, year = {2025},
}
@misc{blog-nosnap,
  title = {Toy Audit Report}, url = {https://audits.example.org/toy-report.pdf},
  note = {Accessed 2026-03-03}, year = {2026},
}
"""


# Synthetic @book entries for the URL fallback; example.org hosts, invented titles.
SELFTEST_BOOK_BIB = r"""
@book{book-url,
  author = {Toy, Ada}, title = {Toy Proofs from Toy Hashes},
  url = {https://github.example.org/toy-proofs-book}, urldate = {2026-10-27}, year = {2024},
}
@book{book-url-nodate,
  author = {Toy, Ada}, title = {Toy Proofs, Second Volume},
  url = {https://books.example.org/toy-2}, year = {2025},
}
@book{book-dead,
  author = {Toy, Ada}, title = {Toy Proofs, Lost Volume},
  url = {https://dead.example.org/toy-3}, urldate = {2026-10-27}, year = {2025},
}
@book{book-doi,
  author = {Toy, Ada}, title = {Toy Proofs with a DOI}, doi = {10.0000/toy.0001},
  url = {https://books.example.org/toy-doi}, year = {2024},
}
@book{book-nourl,
  author = {Toy, Ada}, title = {Toy Proofs Without a Link}, publisher = {Toy Press}, year = {2024},
}
"""


def _selftest_network(plonk: dict) -> None:
    """ePrint/mirror/DOI paths with scripted HTTP answers (polite_http.FakeNet): no real requests."""
    import tempfile
    import eprint_source as es
    from polite_http import FakeNet, PoliteClient, Response
    title = delatex(plonk["fields"]["title"])
    authors = [a.strip() for a in plonk["fields"]["author"].split(" and ")]
    oai = Response("", 200, {}, es._oai(title, authors))
    blocked = Response("", 302, {"location": "https://iacr.org/you_have_been_blocked.txt"}, b"302 Found")
    api = Response("", 200, {}, es._api([es._item("2019/953", title, authors, "2019-08-21")]))

    def crossref(t, au, subtitle=None, year=2019):
        it = {"title": [t], "author": [{"given": a.split()[0], "family": a.split()[-1]} for a in au],
              "issued": {"date-parts": [[year]]}, "DOI": "10.0000/toy"}
        if subtitle:
            it["subtitle"] = [subtitle]
        return Response("", 200, {}, json.dumps({"message": it}).encode())

    def setup(routes, cache_dir=None, **kw):
        net = FakeNet(routes)
        logs = []
        c = PoliteClient(transport=net, clock=net.clock, sleep=net.sleep, cache_dir=cache_dir,
                         use_cache=cache_dir is not None, log=logs.append, **kw)
        polite_http.set_default_client(c)
        return net, {"url_timeout": 3.0, "eprint_source": EprintSource(c, log=logs.append)}, logs

    with_doi = dict(plonk, fields=dict(plonk["fields"], doi="10.0000/toy"))
    try:
        # official ePrint answers: VERIFIED, mirror untouched
        net, st, logs = setup({es.OFFICIAL + "/oai*": [oai]})
        r = check_entry(plonk, False, st)
        assert r["status"] == "VERIFIED" and r["detail"].startswith("ePrint 2019/953:"), r
        assert not any(es.MIRROR in u for _, u in net.calls) and not logs
        # official blocked (observed 302 to the block notice), no DOI: mirror -> VERIFIED (mirror), one notice
        net, st, logs = setup({es.OFFICIAL + "/*": [blocked], es.MIRROR + "/api/search*": [api]})
        r = check_entry(plonk, False, st)
        assert r["status"] == "VERIFIED (mirror)" and "(mirror)" in r["detail"], r
        r2 = check_entry(dict(plonk, key="again"), False, st)
        assert r2["status"] == "VERIFIED (mirror)"
        assert sum(u.startswith(es.OFFICIAL) for _, u in net.calls) == 1        # official tried once per run
        assert sum("third-party mirror" in m for m in logs) == 1
        # official blocked, entry has a DOI: the DOI is used, not the mirror
        net, st, logs = setup({es.OFFICIAL + "/*": [blocked], CROSSREF + "/*": [crossref(title, authors)]})
        r = check_entry(with_doi, False, st)
        assert r["status"] == "VERIFIED" and "checked via DOI" in r["detail"], r
        assert not any(u.startswith(es.MIRROR) for _, u in net.calls)
        # mirror disabled: blocked + no DOI stays UNCHECKED (never NOT_FOUND)
        net, st, logs = setup({es.OFFICIAL + "/*": [blocked]})
        st["eprint_source"].allow_mirror = False
        r = check_entry(plonk, False, st)
        assert r["status"] == "UNCHECKED" and "mirror disabled" in r["detail"], r
        # Crossref 429 + Retry-After: waited out, then VERIFIED
        net, st, logs = setup({CROSSREF + "/*": [Response("", 429, {"retry-after": "9"}),
                                                  crossref(title, authors)]})
        doi_only = dict(plonk, fields={k: v for k, v in with_doi["fields"].items() if k != "howpublished"})
        r = check_entry(doi_only, False, st)
        t = [x for x, _ in net.calls]
        assert r["status"] == "VERIFIED" and t[1] - t[0] >= 9.0, (r, t)
        # cache: the same lookup in a new run makes no request
        with tempfile.TemporaryDirectory() as tmp:
            net, st, _ = setup({CROSSREF + "/*": [crossref(title, authors)]}, cache_dir=tmp)
            check_entry(doi_only, False, st)
            n = len(net.calls)
            net2, st2, _ = setup({CROSSREF + "/*": [crossref(title, authors)]}, cache_dir=tmp)
            assert check_entry(doi_only, False, st2)["status"] == "VERIFIED" and not net2.calls and n == 1
        # request budget: the run stops, the rest is UNCHECKED with a hint
        net, st, logs = setup({CROSSREF + "/*": [crossref(title, authors)]}, max_requests=2)
        many = [dict(doi_only, key=f"k{i}", fields=dict(doi_only["fields"], doi=f"10.0000/toy{i}"))
                for i in range(4)]
        out, stopped = run_entries(many, False, st, quiet=True)
        assert [x["status"] for x in out] == ["VERIFIED", "VERIFIED", "UNCHECKED", "UNCHECKED"], out
        assert stopped and "budget of 2" in stopped and "request budget" in out[2]["detail"]
        # subtitles in a separate field (Crossref `subtitle`, DataCite titleType Subtitle)
        gkr = parse_bib(r"""@article{GKR15, author = {Shafi Goldwasser and Yael Tauman Kalai and Guy N. Rothblum},
          title = {Delegating Computation: Interactive Proofs for Muggles}, doi = {10.0000/gkr}, year = {2015}}""")[0]
        gkr_au = ["Shafi Goldwasser", "Yael Tauman Kalai", "Guy N. Rothblum"]
        net, st, _ = setup({CROSSREF + "/*": [crossref("Delegating Computation", gkr_au,
                                                       "Interactive Proofs for Muggles", 2015)]})
        r = check_entry(gkr, False, st)
        assert r["status"] == "VERIFIED" and r["score"] == 1.0, r
        net, st, _ = setup({CROSSREF + "/*": [crossref("Delegating Computation", gkr_au, year=2015)]})
        assert check_entry(gkr, False, st)["status"] == "MISMATCH"               # without the field: as before
        short = dict(gkr, fields=dict(gkr["fields"], title="Delegating Computation"))
        net, st, _ = setup({CROSSREF + "/*": [crossref("Delegating Computation", gkr_au,
                                                       "Interactive Proofs for Muggles", 2015)]})
        assert check_entry(short, False, st)["status"] == "VERIFIED"             # main title alone still matches
        dc = _datacite_item({"data": {"attributes": {"titles": [
            {"title": "Delegating Computation"}, {"title": "Interactive Proofs for Muggles", "titleType": "Subtitle"}],
            "creators": [{"name": "Goldwasser, Shafi"}], "publicationYear": 2015}}}, "10.0000/gkr")
        assert dc["title"] == "Delegating Computation: Interactive Proofs for Muggles", dc
        assert join_subtitle("Sonic: Zero-Knowledge SNARKs", ["Zero-Knowledge SNARKs"]) == "Sonic: Zero-Knowledge SNARKs"
        # a mirror URL in an entry is flagged
        assert any("mirror URL" in x for x in lint(dict(plonk, fields=dict(
            plonk["fields"], url="https://eprint.iacr.asia/2019/953"))))
    finally:
        polite_http.set_default_client(None)


def run_entries(entries: list[dict], offline: bool, state: dict, quiet: bool = False):
    """Check entries in order; stop at the request budget.  Returns (results, stop message or None)."""
    results, stopped = [], None
    for idx, e in enumerate(entries, 1):
        if stopped:
            r = {"key": e["key"], "type": e["type"], "title": delatex(e["fields"].get("title", ""))[:120],
                 "lint": lint(e), "status": "UNCHECKED", "score": 0.0,
                 "detail": "not checked: request budget reached (re-run; finished lookups are cached)"}
        else:
            try:
                r = check_entry(e, offline, state)
            except polite_http.RequestBudgetExceeded as exc:
                stopped = str(exc)
                if not quiet:
                    print(f"STOP: {exc}", file=sys.stderr)
                r = {"key": e["key"], "type": e["type"], "title": delatex(e["fields"].get("title", ""))[:120],
                     "lint": lint(e), "status": "UNCHECKED", "score": 0.0,
                     "detail": "not checked: request budget reached (re-run; finished lookups are cached)"}
        results.append(r)
        if not quiet:
            print(f"[{idx}/{len(entries)}] {r['status']:9s} {r['key']}", file=sys.stderr)
    return results, stopped


def selftest(online: bool) -> int:
    es = parse_bib(SELFTEST_BIB)
    assert [e["key"] for e in es] == ["GWC19", "fake"], es
    assert es[0]["fields"]["year"] == "2019" and not es[0]["unverified_marker"]
    assert es[1]["unverified_marker"]
    assert find_eprint_id(es[0]["fields"]) == "2019/953"
    assert surnames_from_bib(es[0]["fields"]["author"])[-1] == "ciobotaru"
    assert surnames_from_bib("Malika Izabach{\\`e}ne") == ["izabachene"]
    assert "placeholder author list ('X and others' only)" in lint(es[1])
    assert title_sim("{PLONK}: Permutations over", "PLONK: permutations over") == 1.0
    assert not is_url_source(es[0])            # ePrint-backed @misc keeps the ePrint path
    # URL sources, with injected network fakes (no real requests)
    us = {e["key"]: e for e in parse_bib(SELFTEST_URL_BIB)}
    assert all(is_url_source(e) for e in us.values()), us
    assert entry_url(us["blog-ok"]["fields"]) == "https://blog.example.org/toy-sumcheck"
    assert access_date(us["blog-nosnap"]["fields"]) == "2026-03-03"
    assert explicit_archive(us["blog-nodate"]["fields"]).startswith("https://web.archive.org/web/2025")
    assert "URL source without access date (urldate)" in lint(us["blog-nodate"])
    calls = []

    def fake_probe(url, timeout):
        calls.append(("probe", url, timeout))
        return ("dead." not in url), ("HEAD 200" if "dead." not in url else "GET <urlopen error timed out>")

    def fake_wayback(url, timeout):
        calls.append(("wayback", url, timeout))
        return None if "audits." in url else "http://web.archive.org/web/20260101/" + url

    st = {"delay": 0.0, "url_timeout": 3.0, "probe": fake_probe, "wayback": fake_wayback}
    got = {k: check_entry(e, False, st) for k, e in us.items()}
    assert got["blog-ok"]["status"] == "VERIFIED", got["blog-ok"]
    assert got["blog-nodate"]["status"] == "NEEDS_VERIFICATION" and "no access date" in got["blog-nodate"]["detail"]
    assert got["blog-dead"]["status"] == "NEEDS_VERIFICATION" and "unreachable" in got["blog-dead"]["detail"]
    assert got["blog-nosnap"]["status"] == "NEEDS_VERIFICATION" and "no Wayback" in got["blog-nosnap"]["detail"]
    assert not any(c[0] == "wayback" and "hackmd." in c[1] for c in calls)   # explicit archive URL used
    assert all(c[2] == 3.0 for c in calls)                                    # timeout passed through
    assert check_entry(us["blog-ok"], True, st)["status"] == "UNCHECKED"      # offline stays closed
    assert "| NEEDS_VERIFICATION |" in render(list(got.values()), {})
    # @book with only a URL: title search finds nothing -> URL path (fake searches, no network)
    bs = {e["key"]: e for e in parse_bib(SELFTEST_BOOK_BIB)}
    assert is_url_book(bs["book-url"]) and not is_url_source(bs["book-url"])
    assert not is_url_book(bs["book-doi"]) and not is_url_book(bs["book-nourl"])
    assert "URL source without access date (urldate)" in lint(bs["book-url-nodate"])
    searches = []

    def fake_search(title, *rest):
        searches.append(title)
        return [{"title": "An Unrelated Monograph on Lattices", "authors": ["Nobody Else"], "year": 2020,
                 "source": "fake"}]

    st = {"delay": 0.0, "url_timeout": 3.0, "probe": fake_probe, "wayback": fake_wayback,
          "search_dblp": fake_search, "search_crossref": fake_search}
    rb = check_entry(bs["book-url"], False, st)
    assert rb["status"] == "VERIFIED" and rb["detail"].startswith("@book via URL (title search: fake:"), rb
    assert searches, "title search must run before the URL path"
    rn = check_entry(bs["book-url-nodate"], False, st)
    assert rn["status"] == "NEEDS_VERIFICATION" and "no access date" in rn["detail"], rn
    rd = check_entry(bs["book-dead"], False, st)
    assert rd["status"] == "NEEDS_VERIFICATION" and "unreachable" in rd["detail"], rd
    rx = check_entry(bs["book-nourl"], False, st)
    assert rx["status"] == "NOT_FOUND", rx                                    # no URL: no fallback

    def fake_hit(title, *rest):
        return [{"title": "Toy Proofs from Toy Hashes", "authors": ["Ada Toy"], "year": 2024, "source": "fake"}]

    st_hit = dict(st, search_dblp=fake_hit, search_crossref=fake_hit)
    rh = check_entry(bs["book-url"], False, st_hit)
    assert rh["status"] == "VERIFIED" and "@book via URL" not in rh["detail"], rh   # a record wins
    _selftest_network(parse_bib(SELFTEST_BIB)[0])
    print("selftest (offline part): OK")
    if online:
        polite_http.set_default_client(None)
        st = {"url_timeout": 10.0}
        r0, r1 = check_entry(es[0], False, st), check_entry(es[1], False, st)
        print(f"  online: {r0['key']} -> {r0['status']} ({r0['detail'][:90]})")
        print(f"  online: {r1['key']} -> {r1['status']} ({r1['detail'][:90]})")
        if r0["status"] == "UNCHECKED":
            print("  network unavailable: online part skipped")
        else:
            assert r0["status"] in VERIFIED_STATUSES, r0
            assert r1["status"] in ("NOT_FOUND", "WEAK"), r1
            print("selftest (online part): OK")
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("bib", nargs="?")
    ap.add_argument("--offline", action="store_true", help="static lint only, no network")
    ap.add_argument("--only", help="comma-separated keys to check")
    ap.add_argument("--json", help="write JSON report to this file")
    ap.add_argument("--url-timeout", type=float, default=10.0, help="per-request timeout for URL sources")
    ap.add_argument("--no-mirror", action="store_true",
                    help="never use the third-party ePrint mirror (ePrint-only entries stay UNCHECKED)")
    ap.add_argument("--require-official", action="store_true",
                    help="exit 1 on VERIFIED (mirror) rows too")
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--selftest-online", action="store_true", help="selftest incl. two live lookups")
    polite_http.add_cli_args(ap)
    a = ap.parse_args(argv)
    if a.selftest or a.selftest_online:
        return selftest(a.selftest_online)
    if not a.bib:
        ap.print_usage()
        return 3
    with open(a.bib, encoding="utf-8") as fh:
        entries = parse_bib(fh.read())
    if a.only:
        keep = set(a.only.split(","))
        entries = [e for e in entries if e["key"] in keep]
    c = polite_http.client_from_args(a)
    state = {"url_timeout": a.url_timeout, "no_mirror": a.no_mirror}
    results, stopped = run_entries(entries, a.offline, state)
    src = state.get("eprint_source")
    if src is not None and src.official_down:
        print(f"note: official ePrint unusable ({src.official_down}); entries with a DOI were checked "
              f"through it" + ("" if a.no_mirror else ", the others on the third-party mirror (VERIFIED (mirror))"),
              file=sys.stderr)
    if stopped:
        print(f"note: stopped after {c.requests} requests: {stopped}", file=sys.stderr)
    if not a.offline:
        print(f"note: {c.requests} network requests, {c.cache_hits} cache hits", file=sys.stderr)
    if state.get("dblp_blocked"):
        print("note: DBLP served a bot challenge; title searches used Crossref only", file=sys.stderr)
    dups = duplicate_titles(entries)
    print(render(results, dups))
    if a.json:
        with open(a.json, "w", encoding="utf-8") as fh:
            json.dump({"results": results, "duplicates": dups}, fh, indent=2, ensure_ascii=False)
    ok = ("VERIFIED",) if a.require_official else VERIFIED_STATUSES
    bad = [r for r in results if r["status"] not in ok]
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())

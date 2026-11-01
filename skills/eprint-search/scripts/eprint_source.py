#!/usr/bin/env python3
"""eprint_source.py -- IACR ePrint access with a fallback to a third-party mirror.

Used by eprint_search.py (search) and bib-verify's verify_bib.py (records by id).  All
requests go through polite_http.PoliteClient (spacing, Retry-After, cache, budget).

Official site first.  It counts as *unavailable* for the rest of the run when a request
  - fails to connect or times out (after the client's one connection retry), or keeps
    answering 429/503 after the client's retries;
  - answers with a redirect (3xx).  Observed on 2026-11-01 from a banned client: every
    URL on eprint.iacr.org (incl. /oai) answers `HTTP 302` with
    `Location: https://iacr.org/you_have_been_blocked.txt`, served through Cloudflare,
    with Apache's stock "302 Found ... The document has moved here" body.  The OAI and
    search URLs used here answer 200 directly when the client is not blocked, so any
    redirect is treated as a refusal;
  - answers 403 / 451 / 5xx, or a body that contains "you_have_been_blocked" or
    "has been blocked";
  - answers 200 with a body that is not what the endpoint serves: OAI answers must
    contain "<OAI-PMH", search pages "Cryptology ePrint Archive" (the site name in
    the page template), so a challenge or notice page is not parsed as "no hits".
A 404 is an answer (no such paper), not unavailability.

Then the mirror (default https://eprint.iacr.asia, override with ZKRA_EPRINT_MIRROR):
a public mirror run by a third party, NOT by the IACR.  Searches use its JSON API
`GET /api/search?q=&year=&page=&page_size=` (contract: /openapi.json); a record by id is
looked up with that API (title + year, matched on the ePrint id), and only when the
search does not return the id, with the mirror's OAI-PMH GetRecord.  Every result carries
the official canonical URL https://eprint.iacr.org/YYYY/NNNN; mirror URLs are never
returned for citing.  The switch is announced once per run on stderr, together with the
IACR contact for blocked clients (eprint-abuse@iacr.org).  Nothing here tries to get
around a block: same User-Agent, same IP, no proxy.

    python3 eprint_source.py --selftest    # offline, scripted HTTP answers
"""
from __future__ import annotations

import datetime as dt
import html
import os
import re
import sys
import urllib.error
import urllib.parse

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from polite_http import (HTTPStatusError, PoliteClient, RequestBudgetExceeded,  # noqa: E402
                         Response, default_client)

OFFICIAL = "https://eprint.iacr.org"
MIRROR = os.environ.get("ZKRA_EPRINT_MIRROR", "https://eprint.iacr.asia").rstrip("/")
ABUSE_CONTACT = "eprint-abuse@iacr.org"
OAI_PATH = "/oai?verb=GetRecord&identifier=oai:eprint.iacr.org:{id}&metadataPrefix=oai_dc"
BLOCK_MARKERS = ("you_have_been_blocked", "has been blocked")
SEARCH_MARKER = "Cryptology ePrint Archive"
OAI_MARKER = "<OAI-PMH"


class EprintUnavailable(OSError):
    """Official ePrint refused or did not answer, and the mirror is not allowed / failed."""


def norm_id(eid: str) -> str:
    """'2019/953' -> '2019/953', '2016/21' -> '2016/021' (ePrint pads to three digits)."""
    m = re.fullmatch(r"\s*((?:19|20)\d{2})/(\d{1,5})\s*", eid or "")
    if not m:
        raise ValueError(f"not an ePrint id: {eid!r}")
    return f"{m.group(1)}/{int(m.group(2)):03d}"


def canonical_url(eid: str) -> str:
    return f"{OFFICIAL}/{norm_id(eid)}"


def _strip(s: str) -> str:
    return html.unescape(re.sub(r"<[^>]+>", "", s or "")).strip()


def parse_oai(xml: str, eid: str, via: str) -> dict | None:
    """Dublin Core record -> {title, authors, year, last_year, source, via, url}; None if absent."""
    m = re.search(r"<dc:title>(.*?)</dc:title>", xml, re.S)
    if not m:
        return None
    authors = [html.unescape(x).strip() for x in re.findall(r"<dc:creator>(.*?)</dc:creator>", xml, re.S)]
    date = re.search(r"<dc:date>(\d{4})", xml)
    eid = norm_id(eid)
    return {"title": html.unescape(m.group(1)).strip(), "authors": authors, "year": int(eid[:4]),
            "last_year": int(date.group(1)) if date else None, "via": via, "url": canonical_url(eid),
            "source": f"ePrint {eid}" + (" (mirror)" if via == "mirror" else "")}


_BLOCK = re.compile(r'<a title="(?P<id>\d{4}/\d+)" class="paperlink"(?P<body>.*?)'
                    r'(?=<a title="\d{4}/\d+" class="paperlink"|</main>|\Z)', re.S)


def parse_eprint_search(page: str) -> list[dict]:
    """Official ePrint search page (HTML) -> result rows."""
    out = []
    for m in _BLOCK.finditer(page):
        body = m.group("body")
        title = re.search(r"<strong>(.*?)</strong>", body, re.S)
        authors = re.search(r'<span class="fst-italic">(.*?)</span>', body, re.S)
        upd = re.search(r"Last updated:\s*([0-9-]+)", body)
        cat = re.search(r'class="badge category[^"]*">(.*?)</small>', body, re.S)
        abst = re.search(r'class="mb-0 mt-1 search-abstract">(.*?)</p>', body, re.S)
        out.append({
            "source": "eprint", "via": "official", "id": m.group("id"),
            "url": f"{OFFICIAL}/{m.group('id')}",
            "title": _strip(title.group(1)) if title else "",
            "authors": _strip(authors.group(1)) if authors else "",
            "year": int(m.group("id").split("/")[0]),
            "updated": upd.group(1) if upd else "",
            "category": _strip(cat.group(1)) if cat else "",
            "abstract": _strip(abst.group(1))[:400] if abst else "",
        })
    return out


def mirror_row(it: dict) -> dict:
    """One /api/search item -> a result row with the official canonical URL."""
    eid = norm_id(it["eprint_id"])
    canon = it.get("canonical_url") or ""
    if not canon.startswith(OFFICIAL + "/"):
        canon = canonical_url(eid)
    return {"source": "eprint", "via": "mirror", "id": eid, "url": canon,
            "title": re.sub(r"\s+", " ", it.get("title", "")).strip(),
            "authors": ", ".join(re.sub(r"\s+", " ", a).strip() for a in it.get("authors", [])),
            "authors_list": [re.sub(r"\s+", " ", a).strip() for a in it.get("authors", [])],
            "year": int(it.get("year") or eid[:4]),
            "published": (it.get("published_at") or "")[:10],
            "updated": (it.get("source_datestamp") or "")[:10],
            "category": ", ".join(it.get("subjects") or []),
            "abstract": re.sub(r"\s+", " ", it.get("abstract", ""))[:400]}


class EprintSource:
    def __init__(self, client: PoliteClient | None = None, mirror: str = MIRROR,
                 allow_mirror: bool = True, log=None):
        self.client = client or default_client()
        self.mirror = mirror.rstrip("/")
        self.allow_mirror = allow_mirror
        self.log = log or (lambda msg: print(msg, file=sys.stderr))
        self.official_down: str | None = None     # reason, once detected
        self.used_mirror = False

    # -- official ---------------------------------------------------------------
    @staticmethod
    def official_problem(r: Response, marker: str) -> str | None:
        """Why this answer from eprint.iacr.org means "unavailable", or None if it is usable."""
        if 300 <= r.status < 400:
            loc = r.location or "?"
            if any(m in loc for m in BLOCK_MARKERS):
                return f"HTTP {r.status} to the IACR block notice {loc}"
            return f"HTTP {r.status} redirect to {loc}"
        if r.status == 404:
            return None
        if r.status in (403, 451) or r.status >= 500:
            return f"HTTP {r.status}"
        body = r.text
        if any(m in body for m in BLOCK_MARKERS):
            return "block notice in the answer"
        if r.status == 200 and marker not in body:
            return f"answer is not an ePrint page ({marker!r} missing)"
        return None

    def _mark_down(self, reason: str) -> None:
        if self.official_down:
            return
        self.official_down = reason
        if self.allow_mirror:
            self.log(f"note: official ePrint ({OFFICIAL}) is not usable from this client: {reason}. "
                     f"Using the third-party mirror {self.mirror} for the rest of this run; results "
                     f"cite the official canonical URLs. If the IACR has blocked this address, write to "
                     f"{ABUSE_CONTACT}.")
        else:
            self.log(f"note: official ePrint ({OFFICIAL}) is not usable from this client: {reason}; "
                     f"mirror disabled. If the IACR has blocked this address, write to {ABUSE_CONTACT}.")

    def official_get(self, path: str, marker: str) -> Response | None:
        """GET on the official site; None (and the run switches to the mirror) if unavailable."""
        if self.official_down:
            return None
        try:
            r = self.client.get(OFFICIAL + path)
        except RequestBudgetExceeded:
            raise
        except (urllib.error.URLError, TimeoutError, OSError) as exc:   # incl. HTTPStatusError (429/503)
            self._mark_down(f"request failed ({exc})")
            return None
        reason = self.official_problem(r, marker)
        if reason:
            self._mark_down(reason)
            return None
        return r

    def _need_mirror(self) -> None:
        if not self.allow_mirror:
            raise EprintUnavailable(f"official ePrint not usable ({self.official_down}); mirror disabled")
        self.used_mirror = True

    # -- mirror -----------------------------------------------------------------
    def mirror_search_page(self, q: str | None, year: int | None, page_size: int = 50,
                           page: int = 1) -> dict:
        params = {}
        if q:
            params["q"] = q[:1000]
        if year:
            params["year"] = year
        params["page_size"] = max(1, min(100, page_size))
        if page > 1:
            params["page"] = page
        r = self.client.get(f"{self.mirror}/api/search?{urllib.parse.urlencode(params)}")
        if r.status != 200:
            raise EprintUnavailable(f"mirror search answered HTTP {r.status}")
        try:
            data = r.json()
        except ValueError as exc:
            raise EprintUnavailable(f"mirror search answered non-JSON: {exc}") from exc
        if not isinstance(data, dict) or not isinstance(data.get("items"), list):
            raise EprintUnavailable("mirror search answer has no 'items' list")
        return data

    def mirror_record(self, eid: str, title_hint: str | None = None) -> dict | None:
        eid = norm_id(eid)
        if title_hint and len(title_hint.strip()) >= 2:
            data = self.mirror_search_page(title_hint, int(eid[:4]), page_size=50)
            for it in data["items"]:
                try:
                    same = norm_id(it.get("eprint_id", "")) == eid
                except ValueError:
                    continue
                if same:
                    row = mirror_row(it)
                    return {"title": row["title"], "authors": row["authors_list"], "year": row["year"],
                            "last_year": int(row["updated"][:4]) if row["updated"][:4].isdigit() else None,
                            "via": "mirror", "url": row["url"], "source": f"ePrint {eid} (mirror)"}
        r = self.client.get(self.mirror + OAI_PATH.format(id=eid))
        if r.status == 404:
            return None
        if r.status != 200 or OAI_MARKER not in r.text:
            raise EprintUnavailable(f"mirror OAI answered HTTP {r.status}")
        return parse_oai(r.text, eid, "mirror")

    # -- public API -------------------------------------------------------------
    def official_record(self, eid: str) -> tuple[str, dict | None]:
        """Official OAI only: ("ok", record) | ("missing", None) | ("down", None).
        Lets a caller prefer another source (a DOI) over the mirror when the site is down."""
        r = self.official_get(OAI_PATH.format(id=norm_id(eid)), OAI_MARKER)
        if r is None:
            return "down", None
        if r.status == 404 or "idDoesNotExist" in r.text:
            return "missing", None
        rec = parse_oai(r.text, eid, "official")
        return ("ok", rec) if rec else ("missing", None)

    def fetch_record(self, eid: str, title_hint: str | None = None) -> dict | None:
        """Record for an ePrint id: official OAI, else the mirror.  None = no such paper."""
        state, rec = self.official_record(eid)
        if state != "down":
            return rec
        self._need_mirror()
        return self.mirror_record(eid, title_hint)

    def search(self, query: str, since: str | None = None, title_only: bool = False,
               max_results: int = 50) -> list[dict]:
        params = {"q" if not title_only else "title": query}
        if since:
            params["submittedafter"] = since
        r = self.official_get(f"/search?{urllib.parse.urlencode(params)}", SEARCH_MARKER)
        if r is not None:
            return parse_eprint_search(r.text)
        self._need_mirror()
        # the mirror filters by exact year only: one query per year of the window, then by date
        years = [None]
        if since:
            y0 = int(since[:4])
            years = list(range(max(dt.date.today().year, y0), y0 - 1, -1))
        words = [w for w in re.findall(r"[a-z0-9]+", query.lower()) if len(w) > 1]
        rows = []
        for y in years:
            data = self.mirror_search_page(query, y, page_size=min(100, max_results))
            for it in data["items"]:
                row = mirror_row(it)
                if since and row["published"] and row["published"] < since:
                    continue
                if title_only and not all(w in row["title"].lower() for w in words):
                    continue
                rows.append(row)
        # the mirror ranks metadata and full-text matches alike; put title/abstract matches first
        def relevance(r):
            t, ab = r["title"].lower(), r["abstract"].lower()
            return -(2 * sum(w in t for w in words) + sum(w in ab for w in words))
        return sorted(rows, key=relevance)


# ---------------------------------------------------------------- selftest ---

def _oai(title: str, authors: list[str], date: str = "2019-08-21") -> bytes:
    cr = "".join(f"<dc:creator>{a}</dc:creator>" for a in authors)
    return (f"<?xml version='1.0'?><OAI-PMH><GetRecord><record><metadata><oai_dc:dc>"
            f"<dc:title>{title}</dc:title>{cr}<dc:date>{date}T00:00:00Z</dc:date>"
            f"</oai_dc:dc></metadata></record></GetRecord></OAI-PMH>").encode()


def _api(items: list[dict]) -> bytes:
    import json
    return json.dumps({"items": items, "total": len(items), "page": 1, "page_size": 50, "has_more": False,
                       "next": None, "previous": None, "backend": "sqlite-fulltext",
                       "ranking": "metadata-and-full-text-then-updated",
                       "filters": {"q": "", "category": None, "year": None}}).encode()


def _item(eid: str, title: str, authors: list[str], published: str) -> dict:
    y, n = eid.split("/")
    return {"eprint_id": eid, "year": int(y), "report_number": n, "title": title, "authors": authors,
            "abstract": "Toy abstract.", "subjects": ["Cryptographic protocols"],
            "published_at": published + "T00:00:00Z", "source_datestamp": published + "T00:00:00Z",
            "language": "en", "rights_url": None, "downloaded": False, "file_size": None, "score": 1.0,
            "match_sources": ["metadata"], "url": f"{MIRROR}/{eid}", "pdf_url": None,
            "canonical_url": f"{OFFICIAL}/{eid}"}


def selftest() -> int:
    from polite_http import FakeNet
    toy = "Toy Lookups from Toy Logarithmic Derivatives"
    au = ["Ada Toy", "Bob Example"]
    blocked = Response("", 302, {"location": "https://iacr.org/you_have_been_blocked.txt"},
                       b"<title>302 Found</title><p>The document has moved here.</p>")
    oai_ok = Response("", 200, {}, _oai(toy, au))
    api_hit = Response("", 200, {"content-type": "application/json"},
                       _api([_item("2099/1", "Another Toy", ["C D"], "2099-01-01"),
                             _item("2099/123", toy, au, "2099-03-04")]))

    def make(routes, **kw):
        net = FakeNet(routes)
        logs = []
        c = PoliteClient(transport=net, clock=net.clock, sleep=net.sleep, use_cache=False,
                         min_interval=3.0, log=logs.append)
        return net, EprintSource(c, mirror=MIRROR, log=logs.append, **kw), logs

    # 1. official works: record via official, the mirror is never contacted
    net, src, logs = make({OFFICIAL + "/oai*": [oai_ok]})
    rec = src.fetch_record("2099/123", toy)
    assert rec["via"] == "official" and rec["title"] == toy and rec["authors"] == au, rec
    assert rec["url"] == "https://eprint.iacr.org/2099/123" and not logs and not src.used_mirror
    assert not any(MIRROR in u for _, u in net.calls)
    # 2. official answers the observed 302 to the block notice: switch once, mirror JSON API, canonical URL
    net, src, logs = make({OFFICIAL + "/*": [blocked], MIRROR + "/api/search*": [api_hit]})
    rec = src.fetch_record("2099/123", toy)
    assert rec["via"] == "mirror" and rec["url"] == "https://eprint.iacr.org/2099/123", rec
    assert MIRROR not in rec["url"] and rec["source"].endswith("(mirror)")
    rec2 = src.fetch_record("2099/123", toy)
    assert rec2["title"] == toy
    official_calls = [u for _, u in net.calls if u.startswith(OFFICIAL)]
    assert len(official_calls) == 1, official_calls                 # not retried after the switch
    notes = [m for m in logs if "third-party mirror" in m]
    assert len(notes) == 1 and "you_have_been_blocked" in notes[0] and ABUSE_CONTACT in notes[0], logs
    mt = [t for t, u in net.calls if u.startswith(MIRROR)]
    assert all(b - a >= 3.0 for a, b in zip(mt, mt[1:])), mt          # the mirror is spaced too
    # 3. id not in the search hits -> mirror OAI GetRecord
    net, src, logs = make({OFFICIAL + "/*": [blocked],
                           MIRROR + "/api/search*": [Response("", 200, {}, _api([]))],
                           MIRROR + "/oai*": [oai_ok]})
    assert src.fetch_record("2099/123", toy)["via"] == "mirror"
    assert any("/oai?" in u and u.startswith(MIRROR) for _, u in net.calls)
    # 4. connection failure, 5xx and a non-ePrint 200 page all count as unavailable
    for bad in (urllib.error.URLError("timed out"), Response("", 502, {}, b"bad gateway"),
                Response("", 200, {}, b"<html>Checking your browser...</html>")):
        net, src, logs = make({OFFICIAL + "/*": [bad], MIRROR + "/api/search*": [api_hit]})
        assert src.fetch_record("2099/123", toy)["via"] == "mirror" and src.official_down
    # 5. 404 is an answer: no such paper, no switch
    net, src, logs = make({OFFICIAL + "/*": [Response("", 404, {}, b"")]})
    assert src.fetch_record("2099/999") is None and not src.official_down
    # 6. mirror disabled: blocked official raises instead of falling back
    net, src, logs = make({OFFICIAL + "/*": [blocked]}, allow_mirror=False)
    try:
        src.fetch_record("2099/123", toy)
        raise AssertionError("expected EprintUnavailable")
    except EprintUnavailable:
        assert not any(u.startswith(MIRROR) for _, u in net.calls)
    # 7. the mirror rate-limits us: 429 + Retry-After is honoured, then the answer is used
    net, src, logs = make({OFFICIAL + "/*": [blocked],
                           MIRROR + "/api/search*": [Response("", 429, {"retry-after": "11"}), api_hit]})
    assert src.fetch_record("2099/123", toy)["via"] == "mirror"
    mt = [t for t, u in net.calls if u.startswith(MIRROR)]
    assert mt[1] - mt[0] >= 11.0, mt
    # 8. search: official HTML parsed; blocked -> mirror per year of the window, date filter, title-only filter
    page = (f'<title>Cryptology ePrint Archive</title><a title="2099/123" class="paperlink" href="/2099/123">'
            f'</a><strong>{toy}</strong></main>').encode()
    net, src, logs = make({OFFICIAL + "/search*": [Response("", 200, {}, page)]})
    rows = src.search("toy lookups")
    assert [r["id"] for r in rows] == ["2099/123"] and rows[0]["via"] == "official"
    net, src, logs = make({OFFICIAL + "/*": [blocked], MIRROR + "/api/search*": [api_hit]})
    rows = src.search("toy lookups", since="2099-02-01")
    assert [r["id"] for r in rows] == ["2099/123"], rows             # 2099/1 is older than the window
    assert rows[0]["url"] == "https://eprint.iacr.org/2099/123" and rows[0]["via"] == "mirror"
    years = {urllib.parse.parse_qs(urllib.parse.urlsplit(u).query).get("year", ["-"])[0]
             for _, u in net.calls if u.startswith(MIRROR)}
    assert years == {"2099"}, years
    assert [r["id"] for r in src.search("toy lookups")] == ["2099/123", "2099/001"]   # title match first
    rows = src.search("logarithmic toy", title_only=True)
    assert [r["id"] for r in rows] == ["2099/123"], rows
    assert norm_id("2016/21") == "2016/021" and canonical_url("2019/953") == "https://eprint.iacr.org/2019/953"
    print("selftest: OK (official, blocked->mirror once, OAI fallback, unavailable kinds, 404, "
          "mirror disabled, mirror 429, search)")
    return 0


if __name__ == "__main__":
    if "--selftest" in sys.argv[1:]:
        sys.exit(selftest())
    print(__doc__)

#!/usr/bin/env python3
"""eprint_search.py -- query IACR ePrint (and optionally DBLP / Crossref) from the command line.

Examples
--------
    # novelty check: anything on ePrint in the last 12 months matching the query?
    python3 eprint_search.py "lookup argument logarithmic derivative" --months 12

    # also ask DBLP (published versions, venues), JSON output for scripting
    python3 eprint_search.py "folding scheme" --dblp --json

    # several phrasings of the same idea in one go (union, de-duplicated)
    python3 eprint_search.py "multilinear lookup" "lookup argument sumcheck" --months 24

    python3 eprint_search.py --selftest          # offline: parsers + scripted HTTP answers

Sources
-------
* ePrint search page  https://eprint.iacr.org/search?q=...&submittedafter=YYYY-MM-DD
  (HTML; parsed with regexes -- no third-party deps).  If the official site is not usable
  from this client (connection failure, a redirect such as its 302 to the IACR block
  notice, or a page that is not an ePrint page), the rest of the run uses the third-party
  mirror's JSON API (https://eprint.iacr.asia/api/search; see eprint_source.py) and says so
  once on stderr.  Rows found there have "via": "mirror"; their URL is still the official
  canonical https://eprint.iacr.org/YYYY/NNNN.  --no-mirror turns the fallback off.
* DBLP publication API  https://dblp.org/search/publ/api?q=...&format=json
  (DBLP sometimes serves a bot-challenge page to scripts; this is detected and
  reported, and you should fall back to --crossref.)
* Crossref works API  https://api.crossref.org/works?query.bibliographic=...

Every request goes through polite_http.PoliteClient: >= 3 s between two requests to one
host, Retry-After / backoff on 429 and 503, a per-run request cap and a 7-day answer cache
in .cache/eprint/ (see polite_http.py for the knobs).

Offline behaviour: network errors are reported per source on stderr and the
script exits with status 2 if *no* source answered, so a calling agent can tell
"no hits" (status 0, empty list) from "could not search" (status 2).
"""
from __future__ import annotations

import argparse
import datetime as dt
import html
import json
import os
import sys
import urllib.error
import urllib.parse

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import polite_http  # noqa: E402
from eprint_source import EprintSource, parse_eprint_search  # noqa: E402,F401  (re-exported)

EPRINT = "https://eprint.iacr.org"
DBLP = "https://dblp.org/search/publ/api"


def http_get(url: str) -> str:
    return polite_http.default_client().get_text(url)


_SOURCE: EprintSource | None = None


def eprint_source() -> EprintSource:
    global _SOURCE
    if _SOURCE is None:
        _SOURCE = EprintSource()
    return _SOURCE


def eprint_search(query: str, since: str | None, title_only: bool = False) -> list[dict]:
    return eprint_source().search(query, since, title_only)


# ------------------------------------------------------------------- DBLP ----

class BlockedError(OSError):
    """Service answered with a bot-challenge page instead of data."""


def dblp_search(query: str, hits: int = 30) -> list[dict]:
    url = f"{DBLP}?{urllib.parse.urlencode({'q': query, 'format': 'json', 'h': hits})}"
    raw = http_get(url)
    if raw.lstrip().startswith("<"):
        raise BlockedError("DBLP returned HTML (bot challenge / rate limit); try later or use --crossref")
    data = json.loads(raw)
    out = []
    for h in (data.get("result", {}).get("hits", {}).get("hit") or []):
        info = h.get("info", {})
        au = info.get("authors", {}).get("author", [])
        au = au if isinstance(au, list) else [au]
        out.append({
            "source": "dblp",
            "id": info.get("key", ""),
            "url": info.get("ee") if isinstance(info.get("ee"), str) else (info.get("ee") or [""])[0],
            "title": html.unescape(info.get("title", "")).rstrip("."),
            "authors": ", ".join(a.get("text", "") if isinstance(a, dict) else str(a) for a in au),
            "year": int(info.get("year", 0) or 0),
            "venue": info.get("venue", "") if isinstance(info.get("venue"), str) else ", ".join(info.get("venue", [])),
            "doi": info.get("doi", ""),
        })
    return out


# --------------------------------------------------------------- Crossref ----

CROSSREF = "https://api.crossref.org/works"


def crossref_search(query: str, rows: int = 20) -> list[dict]:
    params = {"query.bibliographic": query, "rows": rows,
              "select": "title,author,DOI,issued,container-title,type"}
    data = json.loads(http_get(f"{CROSSREF}?{urllib.parse.urlencode(params)}"))
    out = []
    for it in data.get("message", {}).get("items", []):
        year = (it.get("issued", {}).get("date-parts") or [[0]])[0][0] or 0
        out.append({
            "source": "crossref",
            "id": it.get("DOI", ""),
            "url": f"https://doi.org/{it.get('DOI', '')}",
            "title": " ".join(it.get("title") or []),
            "authors": ", ".join(f"{a.get('given', '')} {a.get('family', '')}".strip()
                                 for a in it.get("author", [])),
            "year": int(year),
            "venue": " ".join(it.get("container-title") or []),
            "doi": it.get("DOI", ""),
        })
    return out


# ------------------------------------------------------------------- main ----

def render_md(rows: list[dict]) -> str:
    lines = ["| src | id | year | title | authors | venue/updated |", "|---|---|---|---|---|---|"]
    for r in rows:
        tail = r.get("venue") or r.get("updated", "")
        src = r["source"] + (" (mirror)" if r.get("via") == "mirror" else "")
        lines.append(f"| {src} | [{r['id']}]({r['url']}) | {r['year']} | {r['title']} | "
                     f"{r['authors'][:60]} | {tail} |")
    return "\n".join(lines)


def run(queries, months, since, use_dblp, dblp_only, title_only, min_year, use_crossref=False):
    if since is None and months:
        since = (dt.date.today() - dt.timedelta(days=int(months * 30.44))).isoformat()
    rows, answered, seen = [], 0, set()
    for q in queries:
        sources = [] if dblp_only else [("eprint", lambda q=q: eprint_search(q, since, title_only))]
        if use_dblp or dblp_only:
            sources.append(("dblp", lambda q=q: dblp_search(q)))
        if use_crossref:
            sources.append(("crossref", lambda q=q: crossref_search(q)))
        for name, fn in sources:
            try:
                res = fn()
                answered += 1
            except polite_http.RequestBudgetExceeded as exc:
                print(f"STOP: {exc}", file=sys.stderr)
                return rows, answered, since
            except (urllib.error.URLError, TimeoutError, OSError, ValueError) as exc:
                print(f"[offline?] {name} query {q!r} failed: {exc}", file=sys.stderr)
                continue
            for r in res:
                if min_year and r["year"] and r["year"] < min_year:
                    continue
                key = (r["source"], r["id"])
                if key not in seen:
                    seen.add(key)
                    r["query"] = q
                    rows.append(r)
    return rows, answered, since


def selftest() -> int:
    sample = '''<a title="2099/123" class="paperlink" href="/2099/123">2099/123</a>
      <small class="ms-auto">Last updated: 2099-01-02</small></div>
      <strong>Toy Title: &amp; More</strong>
      <div class="mt-1"><span class="fst-italic">Alice A, Bob B</span></div>
      <small class="badge category category-FOUNDATIONS">Foundations</small>
      <p class="mb-0 mt-1 search-abstract">We study toys.</p>
      <a title="2098/7" class="paperlink" href="/2098/7">2098/7</a><strong>Second</strong></main>'''
    rows = parse_eprint_search(sample)
    assert [r["id"] for r in rows] == ["2099/123", "2098/7"], rows
    assert rows[0]["title"] == "Toy Title: & More" and rows[0]["authors"] == "Alice A, Bob B"
    assert rows[0]["updated"] == "2099-01-02" and rows[0]["category"] == "Foundations"
    # run() with scripted HTTP: official ePrint blocked -> mirror rows, canonical URLs; DBLP challenge
    # page -> reported, Crossref still answers; then the request budget stops the run
    import eprint_source as es
    from polite_http import FakeNet, PoliteClient, Response
    global _SOURCE
    item = es._item("2099/123", "Toy Title: & More", ["Alice A", "Bob B"], "2099-03-04")
    net = FakeNet({
        EPRINT + "/*": [Response("", 302, {"location": "https://iacr.org/you_have_been_blocked.txt"})],
        es.MIRROR + "/api/search*": [Response("", 200, {}, es._api([item]))],
        DBLP + "*": [Response("", 200, {}, b"<html>Making sure you are not a bot</html>")],
        CROSSREF + "*": [Response("", 200, {}, json.dumps({"message": {"items": [
            {"title": ["Toy Title"], "DOI": "10.0000/toy", "issued": {"date-parts": [[2099]]}}]}}).encode())]})
    logs = []
    client = PoliteClient(transport=net, clock=net.clock, sleep=net.sleep, use_cache=False, log=logs.append)
    polite_http.set_default_client(client)
    _SOURCE = EprintSource(client, log=logs.append)
    try:
        rows, answered, _ = run(["toy title", "toy more"], None, None, True, False, False, 0, True)
        mir = [r for r in rows if r["source"] == "eprint"]
        assert len(mir) == 1 and mir[0]["via"] == "mirror" and mir[0]["url"] == "https://eprint.iacr.org/2099/123"
        assert answered == 4 and any(r["source"] == "crossref" for r in rows), (answered, rows)
        assert "(mirror)" in render_md(rows) and "eprint.iacr.asia" not in render_md(rows)
        assert sum("third-party mirror" in m for m in logs) == 1
        client.max_requests = client.requests + 1
        rows, answered, _ = run(["third query"], None, None, False, False, False, 0, True)
        assert answered == 1 and [r["source"] for r in rows] == ["eprint"], (answered, rows)  # Crossref stopped
    finally:
        _SOURCE = None
        polite_http.set_default_client(None)
    print("selftest: OK (parser, mirror fallback, DBLP challenge, request budget)")
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("queries", nargs="*", help="one or more query phrasings")
    ap.add_argument("--months", type=float, default=None, help="only ePrint papers submitted in the last N months")
    ap.add_argument("--since", help="only ePrint papers submitted after YYYY-MM-DD")
    ap.add_argument("--title-only", action="store_true", help="ePrint: search titles only")
    ap.add_argument("--dblp", action="store_true", help="also query DBLP")
    ap.add_argument("--dblp-only", action="store_true")
    ap.add_argument("--crossref", action="store_true",
                    help="also query Crossref (published versions with DOI; works when DBLP blocks bots)")
    ap.add_argument("--min-year", type=int, default=0, help="drop hits older than this year")
    ap.add_argument("--no-mirror", action="store_true",
                    help="never use the third-party ePrint mirror (fail if the official site is unusable)")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    polite_http.add_cli_args(ap)
    a = ap.parse_args(argv)
    if a.selftest:
        return selftest()
    global _SOURCE
    _SOURCE = EprintSource(polite_http.client_from_args(a), allow_mirror=not a.no_mirror)
    if not a.queries:
        ap.error("give a query (or --selftest)")
    rows, answered, since = run(a.queries, a.months, a.since, a.dblp, a.dblp_only, a.title_only, a.min_year, a.crossref)
    if answered == 0:
        print("ERROR: no source answered (offline?). Novelty check NOT performed.", file=sys.stderr)
        return 2
    if a.json:
        print(json.dumps({"since": since, "n": len(rows), "results": rows}, indent=2, ensure_ascii=False))
    else:
        print(f"<!-- queries={a.queries} since={since} hits={len(rows)} date={dt.date.today()} -->")
        print(render_md(rows) if rows else "_no hits_")
    return 0


if __name__ == "__main__":
    sys.exit(main())

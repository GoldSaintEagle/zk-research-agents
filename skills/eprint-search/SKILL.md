---
name: eprint-search
description: Search IACR ePrint (with a submission-date window; rate-limited, with a fallback to a third-party mirror when eprint.iacr.org is unreachable) plus Crossref/DBLP from the command line, and run the grey-literature pass (project docs, HackMD, ethresear.ch, vendor blogs, audit reports). Use for novelty checks ("is this idea already taken?"), for building the related-work matrix, and for finding the public ePrint id of a paper before citing it.
---

# eprint-search

## Commands

```bash
S=skills/eprint-search/scripts/eprint_search.py
python3 $S "lookup argument" "logarithmic derivative" --months 12       # union of phrasings, last 12 months
python3 $S "folding scheme" --crossref --min-year 2021                    # + published versions with DOI
python3 $S "sumcheck" --title-only                                        # title search only
python3 $S "..." --json > hits.json                                        # for scripting
python3 $S "..." --no-mirror                                              # official ePrint only
python3 $S --selftest                                                     # offline (scripted HTTP answers)
python3 skills/eprint-search/scripts/polite_http.py --selftest            # rate limiter, offline
python3 skills/eprint-search/scripts/eprint_source.py --selftest          # official/mirror switch, offline
```

Exit status 2 means *no source answered* (offline or blocked) — that is "novelty check not performed", never
"no hits". DBLP sometimes serves a bot challenge to scripts; the script detects it and you should add `--crossref`.

## Rate limits (all literature scripts)

eprint.iacr.org bans addresses that fetch too fast, DBLP serves bot challenges, Crossref drops connections under
load. Every request of `eprint_search.py` and of [bib-verify](../bib-verify/SKILL.md)'s `verify_bib.py` (ePrint,
the mirror below, DBLP, Crossref, DataCite, Wayback, URL probes) goes through one client,
[`scripts/polite_http.py`](scripts/polite_http.py):

| rule | default | change with |
|---|---|---|
| gap between two requests to the same host (kept across runs in the cache folder) | 3 s | `--min-interval`, `ZKRA_HTTP_MIN_INTERVAL` |
| 429 / 503 | wait `Retry-After` (seconds or date; > 300 s is not waited out), else 3 s · 2^k; at most 3 retries | `ZKRA_HTTP_MAX_RETRIES` |
| dropped connection / timeout | one retry after 6 s | — |
| requests per run | 300, then the run stops and says so | `--max-requests`, `ZKRA_HTTP_MAX_REQUESTS` |
| answer cache (200 only, keyed by URL) | 7 days in `.cache/eprint/` (git-ignored) | `--cache-dir`, `--no-cache`, `ZKRA_HTTP_CACHE_TTL` |
| User-Agent | `zk-research-agents/<version> (...; +<repository URL>)`, never a browser string | — |

Do not lower the gap for ePrint, run several copies in parallel, or loop over hundreds of queries: a ban is
long ("permanent unless you can convince us") and hits everyone behind the same address.

## When eprint.iacr.org is unreachable: the mirror

The official site counts as unusable for the rest of a run when a request fails to connect or times out, keeps
answering 429/503, answers with a redirect (a banned client gets `HTTP 302` to
`https://iacr.org/you_have_been_blocked.txt`, observed 2026-11-01), answers 403/451/5xx or a block notice, or
answers a page that is not an ePrint page. The script then says so **once** on stderr and uses the mirror
`https://eprint.iacr.asia` (override: `ZKRA_EPRINT_MIRROR`; disable: `--no-mirror`):

- it is a **third-party** public mirror, not run by the IACR; its data can lag or differ from the archive;
- queries use its JSON API `GET /api/search?q=&year=&page_size=` (contract: `/openapi.json`), never HTML scraping;
  it filters by exact year only, so a `--months` window becomes one query per year plus a date filter, and
  `--title-only` is applied client-side; hits whose title or abstract contain the query words come first;
- rows found there are marked `eprint (mirror)` (`"via": "mirror"` in JSON), and their link is the **official
  canonical URL** `https://eprint.iacr.org/YYYY/NNNN` — cite that one, never a mirror URL (bib-verify lints it);
- the mirror is rate-limited exactly like the official site.

If the official site has blocked your address, the fix is a request to **eprint-abuse@iacr.org** (explain the
tool, its rate limits and the address). Do not work around a block: no new IP, no proxy, no browser User-Agent.

On python.org builds of Python for macOS, HTTPS fails with `CERTIFICATE_VERIFY_FAILED` until the certificates
are installed (`Install Certificates.command`) or `SSL_CERT_FILE=/etc/ssl/cert.pem` is set.

## Novelty-check procedure ("is it already taken?")

1. Write the idea as one falsifiable sentence (what object, what improvement, under which assumptions).
2. Generate **5–10 phrasings**: the technique name, the problem name, the object name, the synonym used by the
   neighbouring community (e.g. "lookup argument" / "lookup" / "table lookup" / "multiset check"), and the
   name of the closest known baseline.
3. Run them with `--months 12` (always) and without a window (for the classic literature). Add `--crossref`
   for published-only venues. Then run the **grey-literature pass** below with the same phrasings.
4. Read the abstract of every hit whose title shares two content words with the idea; open the PDF of any hit
   that shares the object *and* the technique. Snowball: check the "related work" of the 2–3 closest hits and
   the papers that cite the main baseline (Crossref/Google Scholar "cited by").
5. Verdict per idea, logged in `LITERATURE.md` → `## Novelty checks`:
   `- YYYY-MM-DD | query: "..." | sources: eprint,crossref,grey | window: 12m | hits reviewed: N | verdict: clear|overlap:<key>|taken:<key>`
   * `clear`: nothing shares object + technique.
   * `overlap:<key>`: same object or technique, different claim → add a matrix row and a precise "our delta".
   * `taken:<key>`: same claim → stop, tell `pi-orchestrator`; salvage is a new decision, not a rewording.
6. Re-run every 2 weeks while the project is live and once more right before submission (ePrint moves fast;
   the `lit-matrix` linter fails if the newest check is older than 14 days, the P1 gate; P8 requires ≤ 7 days).

## Grey-literature pass (ZK)

Many ZK results appear first, or only, outside ePrint: in project docs, design notes and code. A novelty check
that skips them is incomplete.

| source | how to search | typical content |
|---|---|---|
| project documentation and repos | docs sites, `docs/`/`book/` folders, design notes, RFCs and issues/PRs of the main ZK libraries and zkVMs | new gadgets, arithmetization tricks, PCS variants shipped before a paper |
| HackMD | `site:hackmd.io <phrasing>` | working notes, protocol sketches, benchmark write-ups |
| ethresear.ch | forum search + `site:ethresear.ch <phrasing>` | protocol proposals, folding/recursion ideas, soundness discussions |
| vendor technical blogs | `<phrasing> blog` restricted to the teams behind the baselines in `references/baselines/MANIFEST.md` | prover optimisations, new fields/PCS, benchmark claims |
| public audit reports | the auditor's published report index, the project's `audits/` folder | Fiat–Shamir and circuit pitfalls already known for a design |

Rules:

1. **Window**: the last 24 months for blogs, forums and HackMD (they are rarely superseded cleanly), all time for
   project docs and audit reports of the competitors marked in the matrix. Record the window in the log line.
2. **Provenance**: for every hit you keep, record the URL, the **access date** (YYYY-MM-DD) and an **archived
   copy** (a Wayback Machine snapshot; request one if none exists). Grey sources change or disappear; the archive
   link is what a reviewer can check.
3. **Citing**: a kept hit becomes a `@misc` entry with `url`, `urldate` and the archive link, checked by
   [bib-verify](../bib-verify/SKILL.md); if it cannot be verified it stays marked `needs verification`.
4. **Weight**: a grey source can make an idea `overlap` or `taken` just like a paper. It counts as prior art from
   its earliest verifiable date (archive snapshot, commit date), not from the date you found it.
5. Log grey hits with `sources: ...,grey` in the novelty line; `hits reviewed` counts them too.

## Seeding from the reference books

For older and foundational work (before the 24-month window), the bibliographic notes of the reference books — [CY24 §Bibliographic notes, section:bibliographic-notes] for the hash-based line, and the references of the relevant Thaler chapter (navigation: [references/books/thaler/MAP.md](../../references/books/thaler/MAP.md)) for the algebraic one — are a good source of entries for `references/reading-lists/`. Take only the bibliographic entry (authors, title, venue/ePrint id), never the books' commentary, and add it only after [bib-verify](../bib-verify/SKILL.md) has confirmed it. A book's citation tells you that a
paper exists and what it is about; whether it pre-empts an idea is still decided by reading the paper.

## Pitfalls

- A concurrent ePrint published during your project is normal; record it with its date — reviewers accept
  "concurrent and independent" only if you can show when you knew.
- Do not trust search-engine summaries of a paper's content; read the paper.
- Title-only search misses papers that use a different name for the same object — always also run full-text.

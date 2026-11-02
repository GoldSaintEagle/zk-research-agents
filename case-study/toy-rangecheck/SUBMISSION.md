# SUBMISSION — mock venue (LNCS-format workshop, short paper) — owner: `submission-rebuttal`

Full checklist: `templates/handoff/SUBMISSION.md`. **No real submission** (DECISIONS D-1): nothing leaves the
machine; section E/F are deliberately not done.

## Venue rules
- Mock CFP: LNCS class, ≤ 8 pages excluding references, anonymous, letter or A4. Deadline (illustrative) 2026-12-01.

## A. Format
- [x] LNCS class, no geometry/font changes (`paper/pdf-checks.log`: text width ≈ 12.2 cm)
- [x] within limit: 7 pages in total incl. references and appendix (`pdf_checks.py --limit 8`: RESULT OK)
- [x] no overlap; all fonts embedded (pdf-checks.log)

## B. Anonymity
- [x] `anon_check.py` on sections, main.tex, macros.tex, refs.bib, PDF and figures with a private deny-list (kept
  outside the repository) and the ZK allow-list (`paper/.allow_urls.txt`): HIGH=0 MEDIUM=0 LOW=5 (informational:
  PDF creator/producer, a comment in main.tex) — `paper/anon-check.log`
- [x] PDF metadata empty (title/author/subject/keywords)
- [x] no acknowledgements in the anonymous build

## C. Content consistency
- [x] 0 undefined references; no `<<` placeholders; no `\todo`
- [x] every printed number matched to EVIDENCE: `crbench audit-tex` 0 errors on all 9 .tex files
  (`paper/audit-tex.log`); `gate_check.py --phase P8 --paper paper` PASS (`gate-check.log`)
- [x] abstract ↔ contributions ↔ evaluation use the same numbers (review item D-W1 fixed)
- [x] every contribution maps to a survived/weakened CLAIMS row (C2, C3, C4, C6, C9, C10)

## D. References
- [x] bib-verify: 18/18 VERIFIED (`bib-verify-report.md`, newer than `refs.bib`)

## E/F. Submission form, upload
- [~] not done — mock venue, no upload (D-1)

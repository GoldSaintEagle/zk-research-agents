# zk-research-agents — instructions for Claude Code

This repo is a **toolkit**, not a research project. Research happens in a separate
project directory initialised with `/cra-init <dir>` (see `docs/QUICKSTART.md`).

When working *in a research project* that uses this system:
1. Read `STATE.md` first. The `pi-orchestrator` agent (agents/pi-orchestrator.md) owns phase changes.
2. Hand work between agents **only through blackboard files** (`templates/blackboard/`).
3. Invariants (never break):
   - A statement enters `paper/` only if its `CLAIMS.md` status is `survived` (or `weakened`, using the weakened wording).
   - A number enters `paper/` only if it has an `EVIDENCE.md` row; run `crbench audit-tex paper/main.tex EVIDENCE.md`.
   - A bib entry stays only if `skills/bib-verify` confirmed it exists.
   - Nothing leaves the machine (submission, e-mail, eprint, public repo) without explicit human approval.
4. Prefer `lib/cryptomath` + `lib/bench` over ad-hoc scripts; put throw-away scripts under `falsify/<claim-id>/` or `results/<exp>/`.
5. Toy implementations in `lib/cryptomath/zk|protocols|ec` (sum-check, Merkle, FRI, KZG algebra, permutation/lookup checks, R1CS/Plonkish) are **insecure** and only for reasoning / small experiments.

6. Token discipline (cost, not process: the rules above are unchanged):
   - Command output longer than ~50 lines (builds, benchmarks, test runs, solver and prover logs, verify_bib reports)
     goes to a file under `results/<exp>/` or `falsify/<claim-id>/`; only its tail or a summary enters the context.
   - A subagent returns a bounded summary (about 30 lines at most: verdict, IDs, paths) and puts details in files.
   - Read files by section, not whole, when a row or section is all you need: `grep -n` the ID or term, then `sed -n`
     the range. `STATE.md` is read first; the reference books' GLOSSARY and MAP files have a lookup index at the top.

When working *on this repo*: follow `SPEC.md` (names, formats, the no-private-content rule).

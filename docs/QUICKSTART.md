# Quickstart

## 1. Install
```bash
pip install -e lib/cryptomath -e lib/bench
./install.sh ~/papers/my-new-paper          # copies agents/skills/commands into .claude/
cd ~/papers/my-new-paper && claude
```
For OpenAI Codex: `./install.sh ~/papers/my-new-paper --codex`, then run `codex` there and use `$cra-init`,
`$cra-phase P1`, ... instead of the `/cra-…` commands below (layout and mapping: `AGENTS.md`).
Optional tools the agents use when present: the ZK toolchains you compare against, fetched and pinned with
`references/baselines/fetch.sh` (Rust + cargo for arkworks / halo2 / plonky3 / stwo / binius / nova and the zkVMs,
Go for gnark, circom + snarkjs / rapidsnark with Node, noir / nargo), SageMath, Lean 4 + Mathlib (lean-lsp MCP),
Mathematica MCP, `latexmk` (+ cryptocode, in TeX Live), `pdffonts`, SAT solvers (cadical / kissat) for circuit audits,
Node ≥ 18 for `node --test workflows/tests/`. The reference books are fetched locally, never committed:
`references/books/fetch.sh` (see `references/books/README.md`).

## 2. A typical week-by-week run
| Step | You type | What happens |
|---|---|---|
| 1 | `/cra-init .` | blackboard files + `paper/` skeleton; you give thesis, paper type (protocol / system / application), venue, deadline |
| 2 | `/cra-lit "lookup arguments for range checks"` | lit-scout builds the matrix (ePrint + grey literature), verifies every bib entry, flags pre-emption |
| 3 | `/cra-ideas "range checks dominate the constraint count of our circuit"` | idea-miner runs the 8-step loop, cost-models ideas with constraint-cost / prover-cost-model, registers claims |
| 4 | `/cra-phase P3`, then `/cra-soundness "<protocol>, parameter set A"` | theorist states notions (zk-definitions), proves, checks lemmas numerically; soundness budget computed by theorist and recomputed by falsifier |
| 5 | `/cra-phase P4` then `/cra-bench "<A vs B spec>"` | baselines pinned (full SHA) and signed off at equal soundness; interleaved benchmarks, every proof verified → EVIDENCE |
| 6 | `/cra-circuit-audit <circuit>`, `/cra-fs-audit <protocol>` | builder self-audit, then the falsifier's independent re-run (the one that counts for P6) |
| 7 | `/cra-falsify` | falsifier attacks every open claim; refuted ones go back to P2/P3 |
| 8 | `/cra-write intro`, `/cra-figure "prover time vs number of lookups"` | only survived (or weakened) claims and logged numbers are used |
| 9 | `/cra-review EUROCRYPT protocol` → fix → `/cra-submit` | mock review, anonymisation, checklist, artifact |
| 10 | `/cra-rebuttal reviews.txt 700` | triage + short submitted version + detailed internal version |

At any time: `/cra-status`.

## 3. Heavy multi-agent rounds (optional)
With Claude Code's Workflow tool:
```
Workflow({scriptPath: ".cra/workflows/falsify-round.js", args: {project: "<abs path>"}})
```
Other scripts: `lit-sweep.js`, `idea-tournament.js`, `mock-review-panel.js` (what each does, and the falsify-round
vote rules: `workflows/PHASES.md`).

## 4. Adapting to your group
- Add venue profiles in `skills/venue-calibration/SKILL.md`.
- Add your own baselines to `references/baselines/MANIFEST.md` and `fetch.sh`, then run `references/baselines/fetch.sh --selftest`.
- Seed literature from `references/reading-lists/` (one list per ZK direction).
- Add figure patterns by harvesting your own corpus: `python3 figures/harvester/harvest.py <pdf-dir> --out figures/gallery`.
- New agent: copy any `agents/*.md`, keep the section structure (Mission / Inputs / Outputs / Procedure / Skills / Library / Hand-off / Lessons), and register its blackboard file in `SPEC.md`.

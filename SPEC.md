# SPEC — build contract for zk-research-agents

Every contributor (human or agent) building this repo follows this file.
It is the single source of truth for names, formats and hand-off contracts.

## 0. Hard rules (non-negotiable)

1. **No private research content.** Do NOT copy any unpublished paper title, venue
   submission number, author name, reviewer text, real benchmark number, server address,
   e-mail, review-system transcript, or unpublished theorem from the maintainers' private
   workspaces. Distil *methods* only. Examples must use **toy / synthetic** problems.
   Before every push run `scripts/privacy_scan.sh`, which greps what git would publish (tracked
   files plus untracked, non-ignored ones, and the text and metadata of those PDFs) against a local,
   **git-ignored** deny-list `.privacy-denylist` (one regex per line; each maintainer keeps
   their own; `!<regex>` lines allow values that are public on purpose). Referring to a *public*
   published paper by its public ePrint number is fine. Intentional public values: the fork's
   GitHub URL in the literature scripts' User-Agent (`skills/eprint-search/scripts/polite_http.py`,
   an honest contact for site operators).
2. **No copyrighted PDFs, no harvested figure images** in git. Textbooks appear as
   bibliographic entry + table of contents + topic tags only.
3. **No third-party source trees** in git. Baselines = MANIFEST entry (url, pinned
   commit/tag, build recipe) + fetch script.
4. Every piece of code ships with a test or a runnable `__main__` self-check.
   Python ≥3.10, deps: numpy, sympy, matplotlib, pymupdf (optional), sage (optional,
   guarded import). Toy implementations are marked `# TOY: not secure` at top.
5. Bilingual: English for agent/skill/code/README; Chinese mirror docs in `docs/zh/`.

## 1. Repository layout

```
.claude-plugin/plugin.json   Claude Code plugin manifest
agents/<name>.md             13 subagent definitions (Claude Code format)
skills/<name>/SKILL.md       reusable skills (+ optional scripts/, references/)
commands/<name>.md           slash commands that kick off workflows
workflows/                   phase playbooks + Workflow-tool scripts (*.js)
lib/cryptomath/              Python algorithm library (package `cryptomath`)
lib/bench/                   benchmarking harness (package `crbench`)
lib/lean-template/           Lean4+Mathlib project template
figures/                     mplstyle, template scripts, harvester, gallery index
templates/                   blackboard, paper skeletons, MANIFEST/HANDOFF/rebuttal
references/                  textbook catalog (TOCs), reading lists, baseline MANIFEST
case-study/                  toy end-to-end example run through all phases
docs/                        BIGMAP, quickstart, methodology; docs/zh/ Chinese mirror
AGENTS.md                    Codex / generic-agent entry point (mirrors CLAUDE.md)
CLAUDE.md                    Claude Code entry point
install.sh                   installs agents/skills/commands into a target project (--codex: Codex layout via scripts/codex_export.py)
```

## 2. The 13 agents (file = `agents/<id>.md`)

| id | role | owns blackboard file(s) |
|---|---|---|
| `pi-orchestrator` | phase gates, task dispatch, conflict arbitration; no builder or proposer judges its own claims | `STATE.md`, `DECISIONS.md` |
| `lit-scout` | search (incl. grey literature), related-work matrix, reading notes, concurrent-work watch, **bib verification**; "where is X proved?" from the reference books and textbook index; maintains `references/books/` | `LITERATURE.md`, `refs.bib`, `MATH-REFS.md` |
| `idea-miner` | 8-step idea mining loop with ZK cost proxies | `IDEAS.md` |
| `theorist` | notions and model, PIOP + PCS compilation, proofs, soundness budget, Sage checks, Lean4 formalisation | `THEORY.md`, `lean/` |
| `prover-engineer` | our prover/verifier implementation; cost prediction; FS transcript self-audit | `impl/` |
| `circuit-engineer` | our circuits; constraint counts; circuit self-audit | `circuits/`, `CIRCUITS.md` |
| `baseline-engineer` | fetch/pin/build baselines, recipes, equal-level sign-off | `baselines/MANIFEST.md` |
| `experimenter` | bench protocol, logs → tables, evidence ledger; measures only | `EVIDENCE.md`, `results/` |
| `falsifier` | red team: tries to refute every claim; independent soundness budget and FS/circuit audits; veto power | `CLAIMS.md` (verdict column) |
| `writer` | section-by-section writing via playbook | `paper/` |
| `figure-artist` | figures in house style, harvest good figure patterns | `paper/figs/` |
| `reviewer-sim` | venue-calibrated mock review (ZK reviewer personas) | `REVIEWS.md` |
| `submission-rebuttal` | checklist, anonymisation, artifact, rebuttal, camera-ready | `SUBMISSION.md` |

A protocol/theory project may run without `prover-engineer` and `circuit-engineer` (11 agents).
Builders (`theorist` for its budget, `prover-engineer`, `circuit-engineer`) self-check; only `falsifier`
gives verdicts.

Agent file format (Claude Code subagent):

```markdown
---
name: <id>
description: <when the orchestrator should use it; 1-3 sentences, starts with a verb>
tools: Read, Write, Edit, Bash, Grep, Glob, WebSearch, WebFetch   # least privilege
model: inherit        # or sonnet, see "Model tiers" below
---
# <Title>
## Mission
## Inputs (blackboard files read)
## Outputs (blackboard files written, exact format)
## Procedure (numbered)
## Skills used (links to skills/<name>)
## Library used (lib modules)
## Hand-off contract (what "done" means; which agent is next)
## Failure modes & lessons (distilled, generic)
```

Model tiers (token cost): agents that reason about soundness, judge claims, mine ideas, write the paper or write
the code under audit keep `model: inherit` (pi-orchestrator, theorist, falsifier, idea-miner, writer,
prover-engineer, circuit-engineer). Agents whose work is search, measurement, formatting or checklists use
`model: sonnet` (lit-scout, experimenter, baseline-engineer, figure-artist, submission-rebuttal, reviewer-sim);
reviewer-sim's findings are verified separately and the falsifier re-checks soundness findings. Use the alias
form (`inherit`, `sonnet`, `opus`, `haiku`). `scripts/codex_export.py` drops the key: Codex agents inherit.

## 3. Blackboard (shared state in the *user's research project*, templates in `templates/blackboard/`)

- `STATE.md` — current phase (P0..P8), gate checklist, active tasks, owner.
- `CLAIMS.md` — table: `ID | claim (falsifiable) | proposer | status {open,survived,refuted,weakened} | falsifier evidence | EVIDENCE refs`.
- `EVIDENCE.md` — table: `ID | number/fact as printed in paper | command | log path | commit | machine | date | runs/median`.
  Rule: **no number enters the paper without an EVIDENCE row.**
- `DECISIONS.md` — dated go/no-go decisions with rationale.
- `THEORY.md` — per-result statements (notion, model, proof status, Lean), the assumption ledger, and
  "Parameters and security": one soundness-budget table per parameter set,
  `term | bound ε_i(t) | bits at t = 2^s | proven / conjectured / heuristic | source | EVIDENCE`, with the level
  definition (worst-case or average-case) named, a union-bound total in bits, and conjectured terms kept apart.
- `CIRCUITS.md` — `circuit | arithmetization / backend | constraints or rows (used / padded) | columns | max degree | nonzeros | lookups | EVIDENCE | audit`;
  counts from compiler output, audit cell `none | builder PASS|FAIL <commit> | falsifier PASS|FAIL <commit>`.
- `IDEAS.md`, `LITERATURE.md`, `MATH-REFS.md`, `REVIEWS.md`, `SUBMISSION.md`.

## 4. Phases (workflow)

P0 Scoping → P1 Literature → P2 Ideation → P3 Theory → P4 Baselines → P5 Experiments
→ P6 Falsification gate → P7 Writing+Figures → P8 Review→Submit→Rebuttal→Camera-ready.
Loops: P6 can send back to P2/P3/P5. P8 review can send back to P7/P5.

## 5. Library scope (`lib/cryptomath`)

Subpackages (each with `__init__.py`, docstrings, tests in `lib/cryptomath/tests/`):
- `algebra/` number theory (orders, primitive roots, NTT-friendly primes, roots of unity),
  polynomial rings, GF(p^k) extension fields, radix-2 / Bluestein NTT (butterflies counted).
- `zk/` (TOY, every file `# TOY: not secure`) small-field proof-system components:
  `field` (F_17, F_97, Goldilocks), `mle` (multilinear extensions, eq), `sumcheck`
  (prover/verifier, Fiat–Shamir version, cheating prover for empirical soundness),
  `merkle` (commit, pruned multi-open, collision extraction), `fri` (folding factor, rate,
  queries; proof-size count), `kzg` (algebra only, simulated group with known discrete logs),
  `plonk` (grand-product permutation, logUp lookup), `r1cs` and `plonkish` (representation,
  satisfiability, counts in the CIRCUITS.md conventions).
- `costmodel/` operation counting (`Counter`, `Traced`: nonlinear multiplications = R1CS
  constraints), integer counts of ZK primitives (`zkops`: MSM, NTT, Merkle, sum-check,
  KZG, FRI) and their sympy twins (`formulas`); used to compare provers before implementing.
- `symmetric/` arithmetization-oriented primitive costs (`afcost`: Poseidon/HADES, MiMC, ...)
  and GF(2^n) arithmetic (`gf2n`).
- `protocols/` hash and Pedersen commitments, Fiat–Shamir `Transcript`, Schnorr.
- `ec/` (small) prime-field EC arithmetic, toy groups, generic DLP (BSGS, rho, Pohlig–Hellman).

`zk.{r1cs,plonkish,mle,sumcheck,merkle}` and `costmodel.{counter,zkops}` stay stdlib-only:
`skills/constraint-cost`, `skills/circuit-audit` and `skills/prover-cost-model` import them.

## 6. Bench scope (`lib/bench` → package `crbench`)

Generic harness: interleaved A/B runs, median + IQR + bootstrap CI, warm-up,
CPU pinning / thread control, environment capture (CPU, compiler, commit, flags),
lock file to avoid concurrent benches, log parser registry, LaTeX/Markdown table
generator, EVIDENCE ledger writer, `audit-tex` (ZK units: constraints, rows, gas,
cycles, kB, bits — same as `gate_check.py`). Parsers: generic, criterion (arkworks,
halo2, plonky3), gobench (gnark), gbench, shell-time, snarkjs, rapidsnark, circom,
gnark, nargo-info, risc0, sp1, sat, gnu-time; each ZK parser names its format source
and is tested on synthetic logs. Adapters (recipes, not vendored code; fetch/pin/build in
`references/baselines/MANIFEST.md`) for: arkworks, gnark, circom, snarkjs, rapidsnark,
halo2, plonky3, nargo, RISC Zero, SP1, SAT/SMT solvers (solver-based circuit audits).

## 7. Figures

`figures/style/crypto.mplstyle` (LNCS column widths, colour-blind-safe palette),
`figures/templates/*.py` each producing a PDF+PNG from synthetic data,
`figures/harvester/` — tool that scans a local PDF corpus, extracts figures
(raster + vector clip by caption), classifies by type, scores, and writes a local
gallery (`figures/gallery/` is **gitignored**; only `gallery_index.template.md` and
a *pattern catalog* describing good figure patterns in words are committed).

## 8. Token discipline

Agents, skills, commands and workflow prompts are written so that a run stays cheap without weakening any rule:
- long command output (> ~50 lines) is redirected to a file under `results/` or `falsify/`; only tail/summary is read;
- subagents and workflow agents return bounded summaries (≤ ~30 lines, or a schema) with details in files;
- files are read by section (grep the ID / term / label, then the range), `STATE.md` first; the big reference files
  (`references/books/GLOSSARY.md`, `*/MAP.md`) carry a generated lookup index (`scripts/ref_index.py`);
- mechanical steps (loading rows, ledger writes, bib runs, briefs, merges) use a cheaper model tier
  (`model: sonnet` in front matter or the Workflow `agent()` option), never the steps that judge claims;
- `description` front matter (always loaded) is ≤ ~300 characters, checked at 350 by
  `scripts/check_descriptions.py --selftest`.

## 9. Naming

kebab-case for agents/skills/commands; snake_case for Python modules.

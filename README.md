# zk-research-agents

**A multi-agent research system for zero-knowledge proof papers** — protocol / theory, systems /
implementation and application / circuit papers, from literature search to camera-ready — packaged as
Claude Code agents, skills and slash commands (also usable from Codex via `AGENTS.md`), with a toy ZK
algorithm library, a fair-benchmarking harness, a figure kit and a worked toy example.

A ZK-only fork of [crypto-research-agents](https://github.com/acprk/crypto-research-agents): the process
(blackboard, falsify-first, evidence ledger, P0–P8 gates) is kept; the FHE, lattice and symmetric-cipher
content is replaced by ZK content (soundness budgets, Fiat–Shamir and circuit audits, constraint and
prover cost models, ZK baselines and reading lists).

[中文说明](docs/zh/README.md) · [BIGMAP](docs/BIGMAP.md) · [Quickstart](docs/QUICKSTART.md) · [Case study](case-study/WALKTHROUGH.md)

![BIGMAP](docs/bigmap/bigmap.png)

## Why

Most failed crypto papers do not fail on ideas; they fail on *process*: a claim that was never
attacked, a speedup against the wrong baseline, a number nobody can trace to a log, a reference
that does not exist, a rebuttal that answers the wrong question. This repo encodes a process that
makes those failures structurally hard:

- **Falsify first** — ideas become falsifiable rows in `CLAIMS.md`; a dedicated `falsifier`
  agent (with veto) attacks them before any prose is written.
- **Every number has a log** — `EVIDENCE.md` + `crbench audit-tex` block untraceable numbers.
- **Every reference exists** — `bib-verify` checks bib entries against DBLP/Crossref/ePrint (and URL
  sources for grey literature).
- **Every security level is accounted for** — a soundness-budget table per parameter set, proven and
  conjectured terms kept apart, recomputed independently by the falsifier.
- **Agents talk through files** — a shared blackboard makes hand-offs explicit and auditable.

## What is inside

| Directory | Contents |
|---|---|
| `agents/` | 13 subagents: pi-orchestrator, lit-scout, idea-miner, theorist, prover-engineer, circuit-engineer, baseline-engineer, experimenter, falsifier, writer, figure-artist, reviewer-sim, submission-rebuttal (a protocol / theory project runs without the two engineers) |
| `skills/` | 34 skills. ZK-specific: soundness-budget, zk-definitions, piop-pcs-compile, fiat-shamir-audit, circuit-audit, constraint-cost, prover-cost-model. Process: eprint-search, bib-verify, lit-matrix, reading-notes, textbook-index, idea-mining-loop, sage-check, lean-bridge, baseline-pin, bench-protocol, log-to-evidence, falsify, phase-gate. Writing and submission: paper-playbook (section guides), abstract-craft, technique-overview, related-work-writing, experiments-writing, polish-writing, venue-calibration, mock-review, rebuttal, anonymize-check, camera-ready, artifact-pack, paper-figures, figure-harvest |
| `commands/` | `/cra-init`, `/cra-status`, `/cra-phase`, `/cra-lit`, `/cra-ideas`, `/cra-soundness`, `/cra-circuit-audit`, `/cra-fs-audit`, `/cra-falsify`, `/cra-bench`, `/cra-write`, `/cra-figure`, `/cra-review`, `/cra-rebuttal`, `/cra-submit` |
| `workflows/` | phase playbook P0–P8 with gates + multi-agent Workflow scripts (lit-sweep, idea-tournament, falsify-round, mock-review-panel) and their `node --test` harness |
| `lib/cryptomath/` | toy ZK components (`zk`: small fields, MLE, sum-check, Merkle, FRI, KZG algebra, PLONK permutation / logUp, R1CS, Plonkish), algebra (fields, GF(p^k), NTT), cost models (MSM, NTT, Merkle, sum-check, PCS counts), AO-primitive costs (Poseidon, MiMC, …), protocols (commitments, Fiat–Shamir transcript, Schnorr), small elliptic curves and DLP |
| `lib/bench/` | `crbench`: interleaved A/B runs, robust stats, env capture, parsers for criterion (arkworks / halo2 / plonky3), gnark, snarkjs / rapidsnark, circom, nargo, RISC Zero, SP1, SAT solvers, …, LaTeX tables, EVIDENCE ledger, `audit-tex` (constraints, rows, gas, cycles, kB, bits) |
| `lib/lean-template/` | Lean 4 + Mathlib project template with the proposition ↔ Lean-name table pattern |
| `figures/` | house mplstyles (LNCS/ACM/IEEE), 12 matplotlib + 5 TikZ templates (protocol box, PIOP→PCS pipeline, …), figure harvester + pattern catalog |
| `templates/` | blackboard files (incl. `CIRCUITS.md`, soundness-budget table in `THEORY.md`), LNCS paper skeleton with cryptocode, rebuttal & hand-off templates |
| `references/` | textbook catalog with tables of contents + topic map, reference-book maps for Chiesa–Yogev and Thaler (books fetched locally, never committed), ZK reading lists (PCS, PIOP, lookup, folding, zkVM, Fiat–Shamir, circuit security, PQ / hash-based), baseline MANIFEST (25 ZK libraries) + fetch script |
| `case-study/` | a complete toy project (lookup vs bit-decomposition range checks over Goldilocks, with a planted under-constrained limb the falsifier catches) run through all phases, with real toy measurements |

## Install

```bash
git clone <this repo> ~/zk-research-agents
cd ~/zk-research-agents
pip install -e lib/cryptomath -e lib/bench          # python ≥ 3.10
./install.sh /path/to/my-paper                        # or: ./install.sh --user  (all projects)
```
Or as a Claude Code plugin: `claude plugin install <path-or-url>`.

Then, inside Claude Code in your project:
```
/cra-init .                       # blackboard + paper skeleton
/cra-phase P1                     # literature
/cra-ideas "<bottleneck>"         # idea mining
/cra-falsify                      # red-team every open claim
/cra-status                       # where are we, what next
```
See [docs/QUICKSTART.md](docs/QUICKSTART.md).

## Scope and honesty
- Toy implementations in `lib/cryptomath` are **not secure**; they exist to reason, count and
  sanity-check on small parameters.
- Venue page limits / rebuttal budgets in `skills/venue-calibration` are orientation only —
  always read the current CFP.
- The system never sends anything off your machine (submissions, e-mails, public repos)
  without your explicit approval.
- Literature scripts are rate-limited and identify themselves with the fork's public URL in their
  User-Agent (an honest contact for site operators); they never work around a block.
- Facts not yet checked against a source are marked `needs verification`; the full list is
  [docs/NEEDS-VERIFICATION.md](docs/NEEDS-VERIFICATION.md).

## License
MIT. Reference books are cited and paraphrased only; see `references/books/README.md`.

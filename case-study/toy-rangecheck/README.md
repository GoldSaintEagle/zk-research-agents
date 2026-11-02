# toy-rangecheck — lookup range checks vs bit decomposition (TEACHING EXAMPLE)

A toy research project run through P0–P8 with the 13 agents of this toolkit. Toy parameters (26–30 bits of
soundness), a pure-Python toy prover, a mock venue. **Do not cite any number from here.**
Phase-by-phase narration and the reproduction commands: [`../WALKTHROUGH.md`](../WALKTHROUGH.md).

| path | owner | what |
|---|---|---|
| `STATE.md`, `DECISIONS.md` | pi-orchestrator | thesis v0 → v1, gate checklists P0–P8, decisions D-1…D-8 |
| `LITERATURE.md`, `refs.bib`, `bib-verify-report.md`, `MATH-REFS.md` | lit-scout | 16 papers + 2 reference books, all VERIFIED |
| `IDEAS.md` | idea-miner | I1 (8-bit limbs + logUp) promoted, I2 (16-bit limbs) killed, I3 (running-sum baseline) |
| `THEORY.md`, `theory/` | theorist | lemmas L1–L4 (checked exhaustively), toy argument T1, soundness budgets for every grid point |
| `circuits/` (+ `*/SPEC.md`), `CIRCUITS.md` | circuit-engineer | the three encodings, counts, builder self-audit |
| `impl/` | prover-engineer | toy multilinear Plonkish prover (zero-check + logUp, FS, Merkle), FS self-audit, BUILD.md |
| `baselines/MANIFEST.md` | baseline-engineer | the bits arm on the same backend; equal-level sign-off |
| `code/`, `results/`, `EVIDENCE.md` | experimenter | crbench driver, cost model, ledger rebuilt from raw logs, figure |
| `falsify/`, `CLAIMS.md` | falsifier | one directory per claim group, every attack a script + log; votes tallied with `workflows/falsify-round.js` |
| `paper/` | writer, figure-artist | 7-page LNCS write-up (`main.pdf`), audit-tex / anon-check / pdf-check logs |
| `REVIEWS.md`, `reviews/` | reviewer-sim | round R1, five personas, fix list |
| `SUBMISSION.md` | submission-rebuttal | checklist (no real upload) |
| `gate-check.log` | — | `gate_check.py` output at every phase end, including the re-runs after the P6 and P8 loops |

Outcome (CLAIMS.md): survived C2, C9, C10; weakened C3, C4, C6; refuted C1 (planted under-constrained top limb),
C5 (sub-protocol transcripts not bound to the statement), C7 (R1CS constraints vs Plonkish rows).

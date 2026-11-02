# STATE — toy-rangecheck: lookup range checks vs bit decomposition (TEACHING EXAMPLE)

> Owner: `pi-orchestrator`. Every agent reads this first; only the PI changes `phase`.
> Toy project: insecure parameters, pure-Python toy prover, mock venue. Nothing here is a research result.

- **Phase:** P8 Review → submit (mock) — done
- **Target venue / deadline:** mock venue "LNCS-format workshop, short paper (≤ 8 pp. + refs)"; illustrative deadline 2026-12-01. No real submission (D-1).
- **One-sentence thesis (v0, P0, deliberately too strong):** for range-checking n = 64 values to k bits over
  Goldilocks, the Plonkish + logUp encoding with 8-bit limbs is at least 5× cheaper than bit decomposition —
  in constraints / rows and in prover time — for every k ≤ 64.
- **Thesis (v1, after P6, D-7):** on one toy multilinear Plonkish prover over Goldilocks with n = 64 values and
  8-bit limbs, a logUp range check needs 1/8 of the padded rows of a running-sum bit decomposition and proves
  3.7×–3.8× faster at the grid points 16 ≤ k ≤ 48 (wording corrected at P8, D-8), but never 5×; at k ≤ 12 the 2^8-row table caps the gain (0.96× at k = 4, parity in the reproduction run, D-9).
  k = 64 is not a range check in Goldilocks for either encoding.
- **Last updated:** 2026-11-02 by pi-orchestrator

## Scope (P0)
- **Paper type:** application / circuit paper with a toy system part → all 13 agents (circuit-engineer owns
  `circuits/`, prover-engineer owns `impl/`).
- **Measurable target:** ratio (bits arm / lookup arm) of (a) padded rows and (b) median toy prover CPU time,
  for n = 64, k ∈ {4, 8, 12, 16, 24, 32, 48, 64}, c = 8; target ≥ 5×. Baseline value: the bits arm itself
  (running-sum bit decomposition, the textbook encoding) on the same backend.
- **In scope:** R1CS bit decomposition (counts only), Plonkish running-sum bits, Plonkish + logUp limbs; one toy
  multilinear (sum-check) prover over Goldilocks for both Plonkish arms; constraint/row counts; soundness budget
  of the toy argument; circuit and Fiat–Shamir audits of our own code.
- **Out of scope:** production libraries (halo2, plonky3 …: only cited), zero knowledge (the toy is not
  hiding), polynomial commitments (the toy verifier reads committed columns in the clear), multi-threading,
  absolute timings (pure Python: only ratios on one backend are meaningful, D-1).
- **Resources:** one laptop core, pure Python 3 (numpy for crbench statistics), ≤ 10 min of compute for the whole
  pipeline; time box: one working day for P0–P8.
- **Kill date / criteria:** kill on 2026-11-09 if (i) the two arms cannot run on the same backend (no fair
  comparison), or (ii) the measured spread (IQR/median) exceeds 20 % for either arm after a re-run.

## Gate P0
- [x] thesis is one falsifiable sentence (v0 above; measurable: rows and CPU time ratios, k-grid fixed)
- [x] paper type (application/circuit + toy system) and the agents it needs (all 13)
- [x] measurable target + baseline value (≥ 5×; baseline = running-sum bits arm on the same backend)
- [x] venue CFP read + deadline (mock venue, D-1; nothing is submitted)
- [x] in/out-of-scope list
- [x] compute/time budget
- [x] kill date and kill criteria

## Gate P1
- [x] related-work matrix with ≥ 15 verified works incl. the 2–4 true competitors (LITERATURE.md: 16 works + 2 reference books; competitors in bold: plookup, logUp, cq, Lasso)
- [x] strongest baseline named (bit decomposition with booleanity / running sum, the textbook encoding; Thaler §6.5.4)
- [~] novelty / pre-emption check ≤ 14 days old — WAIVED: teaching example on textbook material, verdict is "taken" by construction (the comparison is folklore, see LITERATURE.md Novelty checks); the live mirror query is logged anyway (DECISIONS D-2)
- [x] refs.bib passes bib-verify (bib-verify-report.md: 16/16 VERIFIED)
- [x] reading notes per competitor (LITERATURE.md, "Reading notes")
- [x] baseline candidates with code status (LITERATURE.md "code?" column; baselines/MANIFEST.md)

## Gate P2
- [x] ≥ 1 idea with a cost-model gain (constraint-cost: rows) and a kill criterion (IDEAS.md I1)
- [x] Gate A (freed parameter: limb width c) and Gate B (anomaly: table height floor) recorded (IDEAS.md)
- [x] top idea registered as falsifiable CLAIMS rows (C1–C6, status open at P2)
- [~] novelty re-check of the chosen idea — WAIVED: same as P1 (DECISIONS D-2)

## Gate P3
- [x] every lemma numerically checked on small params (theory/check_gadgets.py, theory/check_gadgets.log)
- [x] main theorem proof complete; soundness notion, model, setup explicit; assumption ledger (THEORY.md)
- [x] soundness budget table, every term proven/conjectured, level definition named (THEORY.md, results/soundness/)
- [x] lower bound or "none known" (THEORY.md: none known for the toy; Schwartz–Zippel bounds are tight up to constants)

## Gate P4
- [x] strongest baseline builds at a pinned commit (bits arm = same code base, CODE-SHA256 in results/)
- [~] published numbers reproduced within tolerance — WAIVED: the baseline is our own textbook encoding, there is no published number for this toy backend; production libraries are out of scope (DECISIONS D-1, D-4)
- [x] every competitor signed off at the same soundness level as ours (DECISIONS D-4; THEORY.md budgets for both arms)
- [x] build configuration identical to impl/BUILD.md (one interpreter, one process, same flags)

## Gate P5
- [x] protocol fixed before running (results/bench_kscan/README.md)
- [x] interleaved runs, ≥ 3 repeats, medians (crbench, 5 rounds + 1 warm-up, alternating order)
- [x] environment captured (run.json "env")
- [x] every timed run verified its proof (each log prints `verified: True`; failures would stay in run.json)
- [x] every candidate paper number has an EVIDENCE row
- [x] prediction vs measurement compared phase by phase (results/bench_kscan/cost-model.md)

## Gate P6
- [x] no open claims (CLAIMS.md: 3 survived C2/C9/C10, 3 weakened C3/C4/C6, 3 refuted C1/C5/C7)
- [x] refuted claims removed from narrative, weakened wording adopted (thesis v1, D-7)
- [x] soundness budget recomputed independently by the falsifier (falsify/C6_soundness/)
- [x] Fiat–Shamir audit passed in the falsifier's own re-run (falsify/C5_fs/fs-audit.md, after the fix of D-6)
- [x] circuit audit passed in the falsifier's own re-run (falsify/C1_lookup_circuit/circuit-audit.md, after the fix of D-5)
- [x] price of each gain stated (CLAIMS C4 wording: the table floor, the extra logUp columns, 3–4 bits of soundness)
- [x] PI decision logged (DECISIONS D-7)

## Gate P7
- [x] playbook sections complete (paper/sections/*.tex)
- [x] every number ↔ EVIDENCE row (crbench audit-tex: paper/audit-tex.log; gate_check --paper)
- [x] every claim ↔ survived/weakened CLAIMS row
- [x] 0 undefined refs (paper/pdf-checks.log)
- [x] figures from logged data by script in house style (code/make_figures.py)
- [x] related work from the matrix

## Gate P8
- [x] ≥ 1 venue-calibrated mock review, all major points answered (REVIEWS.md R1)
- [x] bib-verify clean on the final bib (bib-verify-report.md)
- [x] anonymisation and page limit checked (paper/anon-check.log, paper/pdf-checks.log)
- [x] artifact builds from a clean checkout (reproduction in ../WALKTHROUGH.md, re-run on 2026-11-02)
- [~] final novelty re-check ≤ 7 days — WAIVED: no real submission (DECISIONS D-1, D-2)

## Active tasks
| task | owner agent | input | expected output | status |
|---|---|---|---|---|
| all phases | see WALKTHROUGH | — | — | done |

## Blockers / questions for the human
- none (nothing leaves the machine; no real submission)

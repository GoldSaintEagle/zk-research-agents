# WALKTHROUGH — toy-rangecheck, phase by phase (TEACHING EXAMPLE)

> **What this is.** A complete, runnable toy ZK research project that shows how the 13 agents of this toolkit
> hand work to each other through the blackboard files, and what each gate checks. The topic is public and
> textbook-level: a k-bit range check for n = 64 values over Goldilocks, written (a) as bit decomposition
> (R1CS, and a Plonkish running-sum gate) and (b) as Plonkish + logUp lookups with 8-bit limbs
> ([Thaler §6.5.4, Details of the Transformation]; [Thaler §6.6.3, Efficiently Representing Non-Arithmetic Operations Over Large Prime-Order Fields]; logUp, ePrint 2022/1530).
> Parameters are insecure (26–30 bits); timings are CPU times of a pure-Python toy prover, so **only ratios
> between the two arms on this one backend mean anything**. Nothing here is a research result.
>
> **How it was produced.** One Claude Code session played every role in turn, following `agents/<id>.md` and
> the skills each agent names; all numbers were measured by the scripts below on 2026-11-02. With the plugin
> installed you drive the same flow with the slash commands shown per phase (or `/cra-phase P<k>`). P6 was run
> by hand following `skills/falsify` (the multi-agent `workflows/falsify-round.js` needs the user's explicit
> opt-in to multi-agent orchestration); the falsifier's lens votes were still tallied with that workflow's tested
> `tally()` (`falsify/tally.mjs`). The run was also the end-to-end acceptance test of the toolkit: the problems it
> found are listed at the end.

Project directory: `case-study/toy-rangecheck/` (blackboard files at its top level; its README maps each
directory to its agent).

## Reproduce

Python ≥ 3.10 with numpy, sympy and matplotlib (e.g. `python3 -m venv .venv && .venv/bin/pip install numpy sympy
matplotlib pymupdf`, then use `.venv/bin/python` as `python3`), Node ≥ 18, a TeX installation with latexmk.
Single core: `export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1`. The code puts `lib/cryptomath` and `lib/bench` on
`sys.path` itself.

**A. Everything that is deterministic (≈ 1 min).** Regenerates every log, table, ledger row, figure and the
PDF from the code and the committed raw benchmark logs; afterwards `git status` should show no change other than
dates, commit hashes, PDF bytes and the cost model's microbenchmarked unit costs (`results/bench_kscan/cost-model.md`,
`prediction.json`).

```bash
cd case-study/toy-rangecheck
python3 circuits/range_gadgets.py && python3 impl/toy_prover.py                 # self-checks (< 1 s)
python3 ../../skills/constraint-cost/scripts/constraint_count.py --n 64 --k 12 --c 4 8 16   # P2 planning counter
python3 theory/check_gadgets.py > theory/check_gadgets.log                      # P3 lemmas, exhaustive
python3 theory/budget.py > results/soundness/summary.md                         # P3 soundness budgets
python3 circuits/selfcheck.py > results/selfcheck/circuits_v2.log               # P5 builder circuit audit
python3 impl/fs_selfaudit.py > results/selfcheck/fs_builder_v2.log              # P5 builder FS audit
python3 code/run_experiments.py --only counts                                   # P5 counts (deterministic)
python3 code/cost_model.py --predict && python3 code/cost_model.py --compare    # P5 prediction vs measurement
python3 falsify/C1_lookup_circuit/audit.py > falsify/C1_lookup_circuit/audit.log   # P6 exhaustive circuit audit (~5 s)
python3 falsify/C5_fs/attack.py > falsify/C5_fs/attack.log                      # P6 FS sensitivity + forgery
python3 falsify/C3_C7_counts/recount.py > falsify/C3_C7_counts/recount.log
python3 falsify/C4_time/recompute.py > falsify/C4_time/recompute.log            # ratios from raw run.json
python3 falsify/C6_soundness/recompute.py > falsify/C6_soundness/recompute.log  # independent budget
node falsify/tally.mjs > falsify/tally.log                                      # verdicts via falsify-round's tally()
python3 code/run_experiments.py --sanitise-only                                 # scrub home dir, user, host, proxy
python3 code/ledger.py                                                          # EVIDENCE.md from raw logs + check
python3 code/make_figures.py                                                    # P7 figure from run.json + counts.log
(cd paper && make)                                                              # P7 PDF (llncs from the TeX tree)
for f in paper/main.tex paper/sections/*.tex; do
  PYTHONPATH=../../lib/bench python3 -m crbench audit-tex "$f" EVIDENCE.md --check-ledger --root .
done                                                                            # every number has a ledger row
python3 ../../skills/camera-ready/scripts/pdf_checks.py paper/main.pdf --log paper/main.log --limit 8
for ph in P0 P1 P2 P3 P4 P5 P6 P7 P8; do
  python3 ../../skills/phase-gate/scripts/gate_check.py --project . --phase $ph --paper paper
done                                                                            # all nine: PASS
```

The anonymity check needs a private deny-list kept outside the repository:
`python3 ../../skills/anonymize-check/scripts/anon_check.py paper/sections paper/main.tex paper/macros.tex refs.bib paper/main.pdf paper/figs --deny-file <your-list> --allow-url-file paper/.allow_urls.txt`.

**B. Re-measure (≈ 1.5 min; numbers vary by a few per cent).** Writes into the git-ignored `results-rerun/`,
so the committed evidence and the paper stay consistent; compare the ratios with `results/*/summary.log`.

```bash
python3 code/run_experiments.py --only bench_kscan --out results-rerun          # P5: 16 arms × (1 + 7) runs
python3 falsify/C4_time/edges.py --out results-rerun                            # P6 edge runs: c = 4/8/16, n = 16
diff <(cut -d' ' -f1,6-8 results/bench_kscan/summary.log) <(cut -d' ' -f1,6-8 results-rerun/bench_kscan/summary.log)
```

**C. Needs the network** (Crossref / ePrint; see `skills/bib-verify` for the mirror fallback):

```bash
python3 ../../skills/bib-verify/scripts/verify_bib.py refs.bib > bib-verify-report.md     # P1/P8: 18/18 VERIFIED
python3 ../../skills/eprint-search/scripts/eprint_search.py "lookup range check" --months 12  # P1 novelty log
```

## The phases

### P0 — Scoping · `/cra-init case-study/toy-rangecheck` then `/cra-phase P0`
- **Agent:** `pi-orchestrator`. **Read:** the one-line topic, `workflows/PHASES.md`.
- **Wrote:** the blackboard from `templates/blackboard/` (what `/cra-init` does); `STATE.md` with thesis v0,
  deliberately too strong: *"for n = 64 values over Goldilocks, logUp with 8-bit limbs is at least 5× cheaper than
  bit decomposition — in constraints/rows and in prover time — for every k ≤ 64"*; paper type
  (application/circuit + toy system → all 13 agents), mock venue, kill date and kill criteria;
  `DECISIONS.md` D-1: both arms on **one** backend we own, only ratios reported.
- **Gate P0:** PASS (7 items).

### P1 — Literature · `/cra-lit "lookup range check"`
- **Agent:** `lit-scout` (skills `lit-matrix`, `bib-verify`, `eprint-search`, `textbook-index`).
- **Read:** `references/reading-lists/lookup.md`, `piop-arithmetization.md`, `circuit-security.md`,
  `fiat-shamir-soundness.md`; the reference books' maps.
- **Wrote:** `LITERATURE.md` (16 works; competitors plookup, logUp, cq, Lasso in bold; reading notes; lint
  `lit_matrix.py` OK), `refs.bib` + `bib-verify-report.md` (**18/18 VERIFIED**, the two books added at P7:
  Thaler via its DOI, CY24 through the URL path with an access date and the archive URL from
  `references/books/README.md`), `MATH-REFS.md` (M1–M10 in the book citation format, checked by
  `scripts/check_book_refs.py`), the novelty query log.
- **Gate P1:** PASS with one waiver (`[~] … WAIVED: … (DECISIONS D-2)`: the trade-off is textbook material).

### P2 — Ideation · `/cra-ideas "lookups vs bits for range checks"`
- **Agent:** `idea-miner` (skill `idea-mining-loop`, cost proxy `constraint-cost`); the `falsifier` screens.
- **Read:** the planning counter `skills/constraint-cost/scripts/constraint_count.py --n 64 --k K --c 4 8 16`.
- **Wrote:** `IDEAS.md` — I1 (8-bit limbs + logUp) promoted; I2 (16-bit limbs) **killed at screening** (the
  2^16 table sets the height); I3 (running-sum gate) adopted as **the baseline**, because the vanilla 3-wire bit
  encoding would inflate the gain. Gate A (freed parameter: limb width c) and Gate B (anomaly: the table-height
  floor at small k). `CLAIMS.md` C1–C7, all `open`. The planning numbers already predicted < 5× at k ≤ 12; the
  claims were kept as written on purpose — the planning counter is not our circuit.
- **Gate P2:** PASS (1 waiver, D-2).

### P3 — Theory · `/cra-phase P3`, `/cra-soundness`
- **Agent:** `theorist` (skills `sage-check`, `zk-definitions`, `soundness-budget`).
- **Wrote:** `THEORY.md`: L1 (running sum = [0, 2^k), unique, if 2^k < p), L2 (limbs + **top-limb check**),
  L2n (without the top-limb check the accepted set is [0, 2^(cL))), L3 (k = 64 in Goldilocks is not a range
  check: 5 and 5 + p both decompose), L4 (logUp counting bound); `theory/check_gadgets.py` (one JSON line per
  statement, exhaustive over F_11 … F_257); T1 (soundness of the toy argument via RBR → state restoration,
  [CY24 §RBR soundness implies SR soundness, theorem:rbr-soundness-to-sr-soundness]); assumption ledger A1–A9;
  `theory/budget.py` writes one `soundness_calc.py` config per grid point and level → `results/soundness/`:
  **26–30 bits worst-case, 48–57 bits average-case** ([CY24 §Security levels, section:security-levels]).
- **Gate P3:** PASS. (The theorist's own table already contradicted C6's "≥ 50 bits average-case"; the claim
  stays open for the falsifier.)

### P4 — Baselines · `/cra-phase P4`
- **Agent:** `baseline-engineer` (skill `baseline-pin`) with `prover-engineer` (`impl/BUILD.md`).
- **Wrote:** `baselines/MANIFEST.md`: the bits arm on the same prover, transcript, field, hash, interpreter and
  timer scope; R1CS flagged *not like-for-like* with Plonkish rows before any number existed; production
  libraries out of scope. D-4: equal-level sign-off (same script, same definition; the lookup arm's extra logUp
  term costs it 3–4 bits).
- **Gate P4:** PASS (1 waiver: no published number exists for this toy backend, D-1/D-4).

### P5 — Build and measure · `/cra-bench "bits vs lookup, k-scan"`, `/cra-circuit-audit`, `/cra-fs-audit`
- **circuit-engineer:** wrote `circuits/range_bits/SPEC.md` and `circuits/range_lookup/SPEC.md` **first**
  (the lookup SPEC lists constraint 4, the top-limb check), then `circuits/range_gadgets.py` — v1 **omits
  constraint 4** (the planted bug). Self-audit `circuits/selfcheck.py`: random differential tests on 203 values per
  k, edge cases, out-of-range inputs (refused by the witness generator) and one mutated cell per gate family —
  **builder PASS**. `CIRCUITS.md` rows, counts from the built objects (`circuits/count.py`).
- **prover-engineer:** `impl/toy_prover.py` (Merkle-committed columns, zero-check over all row constraints,
  logUp helper columns and grand sum, one FS transcript) — v1 calls the library's `sumcheck.prove_fs`, which
  starts a **fresh transcript**. FS self-audit `impl/fs_selfaudit.py`: transcript lint against THEORY's order,
  sensitivity of the **first** challenge, tamper test, domain tags — **builder PASS** (`impl/fs-audit.md`).
  Cost model `code/cost_model.py`: Merkle hashes and sum-check table evaluations per phase, unit costs
  microbenchmarked; the dominant phases (zero-check, commit) land within 1.5× everywhere, the small logUp phase is
  systematically 1.5–1.8× under-predicted and explained (`results/bench_kscan/cost-model.md`).
- **experimenter:** protocol fixed in `results/bench_kscan/README.md` before running; `code/run_experiments.py`
  runs all 16 arms in **one interleaved crbench session** (1 warm-up + 7 rounds, process CPU time, every proof
  verified); `code/ledger.py` rebuilds `EVIDENCE.md` from the raw `run.json`, `counts.log` and the soundness
  outputs (`crbench evidence check`: 0 errors).
- **Gate P5:** PASS with circuits v1 / prover v1 — and again after the P6 loop with v2.

### P6 — Falsification gate · `/cra-falsify` (by hand; votes tallied with `falsify-round.js`'s `tally()`)
- **Agent:** `falsifier` (skills `falsify`, `circuit-audit`, `fiat-shamir-audit`, `soundness-budget`).
  Every attack is a script with its log in `falsify/<claim>/`; lens votes in `falsify/votes.json`.
- **How the planted bug was found.** The falsifier derived its tests from the SPECs, not from the builder's
  report, and re-ran the **real builder** over F_11 and F_13 with k = 3, c = 2 and every assignment of every
  witness cell (`falsify/C1_lookup_circuit/audit.py`): v1 accepts **8, 9, 10** (and has two witnesses for small x).
  In Goldilocks with k = 12 it accepts x = 2^12 with limbs (16, 0). The builder's random differential test could
  not see it — the honest witness satisfies the weaker system — and its out-of-range tests only checked that the
  *generator* refuses. The same audit shows the k = 64 wrap-around in both encodings, and, run on the planning
  counter of `skills/constraint-cost`, found a real toolkit bug (below).
- **What the FS audit found (not planted).** Re-proving honestly with a different statement changes every
  challenge, so it looks fine. Holding the prover's messages fixed and changing only the statement shows that
  the sum-check challenges r_0..r_v do not move: they came from fresh transcripts. `falsify/C5_fs/attack.py` then
  forges proofs of x_0 = 2^k (all-zero messages fix r*, the statement is chosen so that the public column
  vanishes at r*): **4/4 accepted** by the v1 verifier, 0/4 after the fix
  ([CY24 §Lack of adaptive security, section:fs-lack-of-adaptive-soundness]).
- **Loops back to P5:** D-5 (circuits v2: one extra shifted lookup per value when 8 ∤ k; the builder adds the
  exhaustive check to its self-audit), D-6 (prover v2 continues the outer transcript through the library's new
  `transcript=` argument); counts and the benchmark re-run, v1 summaries kept in `results/superseded/` without
  EVIDENCE rows.
- **Other attacks:** ratios recomputed from raw `run.json` (C4); counts recomputed (C3, C7); an edge session over
  limb width and statement size (`falsify/C4_time/edges.py`: c = 4 → 2.07×, c = 16 → 0.04×, n = 16 → 1.05×); an
  independent budget from the code's actual layout plus a challenge-sampling bias term (C6, agrees with THEORY at
  every point).

| claim | verdict | how it was decided |
|---|---|---|
| C1 lookup circuit correct, k ≤ 64 | **refuted** | exhaustive audit of v1 (planted bug) + k = 64 wrap-around |
| C2 bit decompositions correct, k ≤ 63 | **survived** | exhaustive F_11/F_13 (Plonkish and R1CS), L1 |
| C3 padded rows ≥ 5× fewer, every k ≤ 64 | **weakened** | 8× for 16 ≤ k ≤ 63, 4× at k = 8, 12, 2× at k = 4 (table floor) |
| C4 prover time ≥ 5× faster, every k ≤ 64 | **weakened** | below 5× everywhere: 3.7×–3.8× for 16 ≤ k ≤ 48, no faster at k = 4 (0.96×; 1.00× in the reproduction run); price stated |
| C5 transcript passes FS audit | **refuted** | sub-transcripts unbound; 4/4 forgeries |
| C6 ≥ 25 bits worst / ≥ 50 bits average | **weakened** | recomputed: ≥ 26 worst, ≥ 48 average |
| C7 ≥ 5× fewer constraints than R1CS | **refuted** | unit mismatch (constraint-cost §1); 2.5× even naively at k = 4 |
| C9 v2 lookup circuit correct, k ≤ 63 | **survived** | exhaustive F_11/F_13/F_17, x = 2^12 rejected |
| C10 v2 transcript binds every challenge | **survived** | fixed-message sensitivity, 0/4 forgeries |

- **Gate P6:** PASS. D-7 adopts thesis v1 (STATE.md).

### P7 — Writing + figures · `/cra-write <section>`, `/cra-figure "advantage vs k"`
- **Agents:** `writer` (skill `paper-playbook`), `figure-artist` (skill `paper-figures`, pattern P12 of
  `figures/PATTERNS.md`, `figures/style/palette.py`).
- **Wrote:** `paper/` from `templates/paper/` (LNCS, anonymous); numbers carry `\evid{E…}` tags;
  `code/make_figures.py` draws the figure from `run.json` and `counts.log` only; `main.pdf`, 7 pages.
- **Checks:** `crbench audit-tex` on all nine .tex files: 0 errors (`paper/audit-tex.log`); `gate_check.py
  --paper` PASS. Definitions (the 5× target, the CI level, protocol parameters, 2^16 as a table size) carry
  `% no-evidence: <reason>`, which both checkers now accept.
- **Gate P7:** PASS (and again after the P8 loop).

### P8 — Review → submit (mock) · `/cra-review "LNCS workshop"`, `/cra-submit`
- **Agents:** `reviewer-sim` (skills `venue-calibration`, `mock-review`), `submission-rebuttal` (skills
  `anonymize-check`, `camera-ready`).
- **Wrote:** `reviews/REVIEW-BRIEF.md`; `REVIEWS.md` round R1 with the application reviewer (mandatory for the
  paper type), the soundness reviewer, the implementation-and-benchmark reviewer and the optional data and
  desk-reject auditors (scores 4 / 4 / 3). The data auditor found a real inconsistency: the abstract printed
  "3.69×–3.98× for 16 ≤ k ≤ 63", but 3.98× is the k = 64 point — and C4's weakened wording had the same slip.
  D-8 routed it to the falsifier (re-issued wording) and the writer; the implementation reviewer's missing-PCS
  limitation and the edge-run numbers (new EVIDENCE rows E40–E43) went in too. `reviews/SUBMIT-FIXES.md`;
  `SUBMISSION.md`; `anon_check.py` HIGH=0 MEDIUM=0 LOW=5; `pdf_checks.py` RESULT OK. Nothing was uploaded.
- **Gate P8:** PASS (1 waiver: final novelty re-check, no real submission).

## Toolkit problems this run found (fixed in the same batch)

| problem | found at | fix |
|---|---|---|
| `gate_check.py` could not read the shipped templates: CLAIMS "EVIDENCE / THEORY refs" and EVIDENCE "value as printed" columns were not found, so every survived claim and every paper number failed | P5/P7 | column lookup by header words; selftest runs on the real templates |
| `templates/blackboard/EVIDENCE.md` had 9 columns, while `crbench evidence add` and `soundness_calc.py --evidence` write the 8 SPEC §3 columns (rows landed shifted) | P5 | template uses the SPEC header |
| `gate_check.py` compared spellings: `3.88\times` ≠ `3.88×`; `2^{2c}` was read as the number `2^{2` | P7 | normalised spellings; symbolic exponents ignored |
| `crbench audit-tex` read the range dash in `3.69$\times$--3.98$\times$` as a minus sign | P7 | a sign never follows another `-` |
| the two checkers had different escape hatches (`% no-evidence:` vs `% crbench:ignore`) | P7 | each accepts the other's |
| the paper template tagged numbers with `\ev{…}`; crbench only checks `\evid{…}` | P7 | template uses `\evid` |
| `lib/cryptomath` `sumcheck.prove_fs/verify_fs` could only start a fresh transcript, so a sum-check sub-protocol could not be bound to the statement | P6 | `transcript=` argument, test with the forgery |
| `constraint_count.py::plonk_lookup` (planning counter) left `acc_0` free — it accepted every x — and the last row's limb cell unconstrained | P6 | `zero` gate, no padding cell, selftest |
| `toy_fs_attack.py::transcript_lint` could not handle an item kind absorbed in two rounds | P5 | subsequence matching, selftest |
| the fiat-shamir-audit procedure's sensitivity test (first challenge, honest re-proving) cannot see unbound sub-transcripts | P6 | procedure and pitfalls updated |
| `soundness_calc.py --evidence` left the log path as a placeholder | P3 | `--log PATH` |
| the anonymity allow-list template did not contain the reference book's own URL | P8 | added |

## What to copy from this example into a real project
1. Write the strong thesis first and let the falsifier cut it down; keep the refuted rows (C1, C5, C7).
2. Write each gadget's SPEC before its constraints, and audit the **real builder** exhaustively on a small field:
   random and "generator refuses" tests cannot find a missing constraint.
3. Test Fiat–Shamir sensitivity with the prover's messages held fixed, for every challenge, sub-protocols
   included; a library default (a fresh transcript) is not a neutral choice.
4. Compare encodings in one unit on one backend; a lookup table occupies rows, so check the small end of the range.
5. Attack the edges of what a claim quantifies over (here k = 64, k = 4, c = 16, n = 16), not the points measured.
6. Let a data auditor recompute every printed range against the claim's domain — the k = 64 point slipped into
   "16 ≤ k ≤ 63" twice.
7. Re-run the gate after every loop (P6 → P5, P8 → P7); `gate-check.log` keeps the history.

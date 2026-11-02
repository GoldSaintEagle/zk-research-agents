# Circuit audit — range_bits / range_lookup, case-study toy-rangecheck, field Goldilocks (F_11 / F_13 / F_17 models), auditor: falsifier

Specs: `circuits/range_bits/SPEC.md`, `circuits/range_lookup/SPEC.md` (tests derived from these, not from the builder's
report). Script and output: `audit.py`, `audit.log` (this directory).

| gadget | spec | uniqueness | under | over | ranges | wrap | hints | public inputs | method | evidence |
|---|---|---|---|---|---|---|---|---|---|---|
| ~~range_lookup v1 (c = 8)~~ | ~~x < 2^k~~ | ~~FAIL~~ | ~~FAIL: accepts 8, 9, 10 (F_11, k = 3, c = 2); x = 2^12 at k = 12 in Goldilocks~~ | ~~PASS~~ | ~~FAIL: top limb not limited to r bits (SPEC 4)~~ | — | n.a. | ~~PASS~~ | ~~exhaustive F_11, F_13 + real-field witness~~ | ~~audit.log lines 2–3, 14~~ |
| range_lookup v2 | x < 2^k, 1 ≤ k ≤ 63 | PASS | PASS | PASS | PASS (top-limb lookup) | 2^k < p required; **k = 64 FAILS** (5 and 5 + p) | n.a. | last acc copied to x_j | exhaustive F_11, F_13 (c ∤ k), F_17 (c ∣ k) + real field | audit.log |
| range_bits (Plonkish) | x < 2^k, 1 ≤ k ≤ 63 | PASS | PASS | PASS | n.a. | k = 4 over F_11 (2^k > p): NON-UNIQUE, as predicted (L3); k = 64 in Goldilocks: two witnesses for x = 5 | n.a. | last acc copied | exhaustive F_11, F_13 + real field | audit.log |
| range_bits (R1CS) | x < 2^k | PASS | PASS | PASS | n.a. | as above | n.a. | x_j public variable | exhaustive F_11, F_13 | audit.log |

Also found (harness calibration, outside our circuits): `skills/constraint-cost/scripts/constraint_count.py::plonk_lookup`
accepted every x (no `acc_0 = 0` constraint) and left the last row's limb cell free; the first run of this audit
printed `FAIL: UNDER-CONSTRAINED; NON-UNIQUE WITNESS — accepts out-of-spec [4, 5, 6, 7, 8, 9, 10]; #witnesses
[(0, 44), …]` for k = 2, c = 2 over F_11. Fixed in the toolkit (case-study batch); audit.log line 12 now reads PASS.

Verdict: v1 FAIL (C1 refuted); v2 PASS for 1 ≤ k ≤ 63 (C9 survived); k = 64 is outside every circuit's spec.

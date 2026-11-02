# IDEAS — output of `idea-miner` (P2)

Planning numbers: `skills/constraint-cost/scripts/constraint_count.py --n 64 --k K --c 4 8 16`
(log: `results/planning/constraint_count.log`). These are toy-counter numbers: they screen ideas and never
enter the paper (constraint-cost §6).

Pre-gate sentence (security-bearing vs substrate): the range check is **security-bearing** — an
under-constrained range check makes the argument prove a false statement — so every encoding idea comes with a
circuit claim that the falsifier audits, not only a cost claim.

## I1: 8-bit limbs + logUp lookups instead of bit decomposition
- **Probe / anomaly observed:** bit decomposition costs n(k+1) rows; limbs cost n(⌈k/c⌉ + 1) rows plus a
  2^c-row fixed table. Planning, n = 64, c = 8: padded height 512 → 256 (k = 4), 1024 → 256 (k = 8, 12),
  2048 → 256 (k = 16), 4096 → 512 (k = 32), 8192 → 1024 (k = 64).
- **Algebraic / structural explanation:** one lookup replaces c booleanity rows; the price is the table, the
  multiplicity column and the logUp helper columns.
- **Controlled experiment:** same toy multilinear prover for both arms, k-grid {4, 8, 12, 16, 24, 32, 48, 64},
  n = 64; count rows, measure prover CPU time (bench-protocol).
- **Expected gain (cost model):** height ratio 2× (k = 4), 4× (k = 8, 12), 8× (k ≥ 16) from the counter; the
  prover-time ratio should be lower (more columns per row on the lookup side).
- **Kill criteria:** if the prover-time ratio is < 1 for every k, or the two arms cannot run on the same
  backend.
- **Pre-emption check:** textbook trade-off (LITERATURE.md, D-2).
- **Status:** promoted to CLAIMS (C1, C3, C4, C7; the PI's thesis wording is kept on purpose so the falsifier can
  cut it).

## I2: 16-bit limbs (fewer lookups)
- **Probe:** c = 16 halves the lookups at k = 64.
- **Explanation:** the table now has 2^16 rows, which sets the height for every n·k in our grid (65536 vs ≤ 8192
  for the bits arm).
- **Expected gain:** negative for n = 64 (height 8× *larger* than bits at k = 64).
- **Kill criteria / status:** **killed at screening** (falsifier, P2): the planning counter already shows the
  table floor. Kept as the motivation for the falsifier's limb-width edge case in P6.

## I3: running-sum custom gate for the bits arm (the strongest baseline)
- **Probe:** vanilla 3-wire bits need n(2k − 1) rows; a degree-2 running-sum gate needs n(k + 1) rows on one
  column.
- **Status:** adopted as **the baseline** (comparing against the weaker vanilla encoding would inflate our gain;
  baseline-pin rule "strongest baseline").

## Gate A (freed parameter) and Gate B (anomaly)
- **Gate A:** the freed parameter is the limb width c: lookups trade c booleanity rows for table rows.
- **Gate B:** anomaly in the planning numbers: at small k the ratio is bounded by the table, not by k (height
  floor 2^c). Recorded; it is the edge the falsifier should attack first.

## Falsifier screening at P2 (before claims are registered)
- I2 killed (table floor).
- Thesis wording "for every k ≤ 64": the planning numbers already predict < 5× at k ≤ 12 in rows. Kept as an
  `open` claim (C3) because the planning counter is not our circuit; P5 measures our circuits, P6 decides.
- "Cheaper in constraints" vs R1CS: flagged as a unit mismatch (R1CS constraints vs Plonkish rows), registered as
  its own claim (C7) so the verdict is explicit.

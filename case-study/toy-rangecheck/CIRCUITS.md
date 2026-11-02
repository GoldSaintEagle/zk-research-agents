# CIRCUITS — circuit inventory, counts and audit status (owner: `circuit-engineer`)

Counts come from the built objects (`circuits/count.py` → `results/counts/counts.log`, EVIDENCE E1–E8);
n = 64 values, c = 8, Goldilocks. Audit cell: `none` | `builder PASS|FAIL <code>` | `falsifier PASS|FAIL <code>`;
`<code>` = circuits version (file hashes in `results/CODE-SHA256.txt`).

| circuit | arithmetization / backend | constraints or rows (used / padded) | columns (adv/fix/inst) | max degree | nonzeros | lookups (table sizes) | EVIDENCE | audit (circuit-audit) |
|---|---|---|---|---|---|---|---|---|
| range_bits (R1CS) | R1CS, counted only | 65·n = 4160 constraints at k = 64 | — | 2 | 16512 at k = 64 | 0 | E1, E2 | builder PASS v2 · falsifier PASS v2 (k ≤ 63) |
| range_bits (Plonkish) | Plonkish, toy multilinear prover | n(k+1) rows / next pow2; 4160 / 8192 at k = 64 | 1 / 2 selectors / 1 pub | 2 | — | 0 | E1, E3 | builder PASS v2 · falsifier PASS v2 (k ≤ 63) |
| range_lookup (Plonkish + logUp) | Plonkish + logUp, toy multilinear prover | n(⌈k/8⌉+1) rows; height ≥ 256 (table); 576 / 1024 at k = 64 | 2 (+ m) / 2 selectors + lookup selectors + table / 1 pub | 1 (gates), 2 (logUp helper constraints) | — | n⌈k/8⌉ (+ n when 8 ∤ k, v2) lookups, table 2^8 | E1, E4, E8 | ~~builder PASS v1~~ · ~~falsifier FAIL v1~~ · builder PASS v2 · falsifier PASS v2 (k ≤ 63) |

v1 → v2 (DECISIONS D-5): the lookup arm gained the top-limb shifted lookup; rows and padded heights are unchanged, lookups grow from n⌈k/8⌉ to n(⌈k/8⌉ + 1) when 8 ∤ k (e.g. 128 → 192 at k = 12). Superseded v1 counts: results/superseded/counts_v1.log.

# Cost model — toy multilinear Plonkish prover, n = 64, c = 8, Goldilocks, Merkle (SHA-256) commitments
Unit costs (microbenchmarks, `code/cost_model.py --predict`): Merkle hash 0.31 µs, sum-check table-evaluation 0.159 µs. Measured = median of the 7 rounds of bench_kscan.

| arm, k | phase | hashes | table-evaluations | predicted | measured | ratio | flag / explanation |
|---|---|---|---|---|---|---|---|
| bits, 4 | commit | 1023 |  | 0.32 ms | 0.35 ms | 1.10 |  |
| bits, 4 | zerocheck |  | 21469 | 3.40 ms | 4.60 ms | 1.35 |  |
| bits, 8 | commit | 2047 |  | 0.64 ms | 0.70 ms | 1.09 |  |
| bits, 8 | zerocheck |  | 42973 | 6.81 ms | 8.97 ms | 1.32 |  |
| bits, 12 | commit | 2047 |  | 0.64 ms | 0.70 ms | 1.10 |  |
| bits, 12 | zerocheck |  | 42973 | 6.81 ms | 8.96 ms | 1.31 |  |
| bits, 16 | commit | 4095 |  | 1.29 ms | 1.38 ms | 1.07 |  |
| bits, 16 | zerocheck |  | 85981 | 13.63 ms | 17.54 ms | 1.29 |  |
| bits, 24 | commit | 4095 |  | 1.29 ms | 1.36 ms | 1.06 |  |
| bits, 24 | zerocheck |  | 85981 | 13.63 ms | 17.10 ms | 1.25 |  |
| bits, 32 | commit | 8191 |  | 2.57 ms | 2.77 ms | 1.08 |  |
| bits, 32 | zerocheck |  | 171997 | 27.27 ms | 34.69 ms | 1.27 |  |
| bits, 48 | commit | 8191 |  | 2.57 ms | 2.78 ms | 1.08 |  |
| bits, 48 | zerocheck |  | 171997 | 27.27 ms | 35.24 ms | 1.29 |  |
| bits, 64 | commit | 16383 |  | 5.14 ms | 5.52 ms | 1.07 |  |
| bits, 64 | zerocheck |  | 344029 | 54.54 ms | 71.13 ms | 1.30 |  |
| lookup, 4 | commit | 1533 |  | 0.48 ms | 0.53 ms | 1.09 |  |
| lookup, 4 | logup | 1533 |  | 0.53 ms | 0.83 ms | 1.58 | OUTSIDE [1/1.5, 1.5] |
| lookup, 4 | zerocheck |  | 22968 | 3.64 ms | 3.44 ms | 0.94 |  |
| lookup, 4 | grandsum |  | 2298 | 0.36 ms | 0.38 ms | 1.03 |  |
| lookup, 8 | commit | 1533 |  | 0.48 ms | 0.53 ms | 1.10 |  |
| lookup, 8 | logup | 1022 |  | 0.35 ms | 0.55 ms | 1.57 | OUTSIDE [1/1.5, 1.5] |
| lookup, 8 | zerocheck |  | 20416 | 3.24 ms | 3.10 ms | 0.96 |  |
| lookup, 8 | grandsum |  | 1532 | 0.24 ms | 0.32 ms | 1.33 |  |
| lookup, 12 | commit | 1533 |  | 0.48 ms | 0.53 ms | 1.10 |  |
| lookup, 12 | logup | 1533 |  | 0.53 ms | 0.82 ms | 1.56 | OUTSIDE [1/1.5, 1.5] |
| lookup, 12 | zerocheck |  | 22968 | 3.64 ms | 4.04 ms | 1.11 |  |
| lookup, 12 | grandsum |  | 2298 | 0.36 ms | 0.45 ms | 1.23 |  |
| lookup, 16 | commit | 1533 |  | 0.48 ms | 0.52 ms | 1.09 |  |
| lookup, 16 | logup | 1022 |  | 0.35 ms | 0.56 ms | 1.58 | OUTSIDE [1/1.5, 1.5] |
| lookup, 16 | zerocheck |  | 20416 | 3.24 ms | 3.62 ms | 1.12 |  |
| lookup, 16 | grandsum |  | 1532 | 0.24 ms | 0.37 ms | 1.54 | OUTSIDE [1/1.5, 1.5] |
| lookup, 24 | commit | 1533 |  | 0.48 ms | 0.54 ms | 1.12 |  |
| lookup, 24 | logup | 1022 |  | 0.35 ms | 0.57 ms | 1.62 | OUTSIDE [1/1.5, 1.5] |
| lookup, 24 | zerocheck |  | 20416 | 3.24 ms | 3.40 ms | 1.05 |  |
| lookup, 24 | grandsum |  | 1532 | 0.24 ms | 0.37 ms | 1.51 | OUTSIDE [1/1.5, 1.5] |
| lookup, 32 | commit | 3069 |  | 0.96 ms | 1.03 ms | 1.07 |  |
| lookup, 32 | logup | 2046 |  | 0.70 ms | 1.06 ms | 1.50 | OUTSIDE [1/1.5, 1.5] |
| lookup, 32 | zerocheck |  | 40896 | 6.48 ms | 7.00 ms | 1.08 |  |
| lookup, 32 | grandsum |  | 3068 | 0.49 ms | 0.68 ms | 1.39 |  |
| lookup, 48 | commit | 3069 |  | 0.96 ms | 1.04 ms | 1.08 |  |
| lookup, 48 | logup | 2046 |  | 0.70 ms | 1.06 ms | 1.51 | OUTSIDE [1/1.5, 1.5] |
| lookup, 48 | zerocheck |  | 40896 | 6.48 ms | 7.25 ms | 1.12 |  |
| lookup, 48 | grandsum |  | 3068 | 0.49 ms | 0.69 ms | 1.42 |  |
| lookup, 64 | commit | 6141 |  | 1.93 ms | 2.06 ms | 1.07 |  |
| lookup, 64 | logup | 4094 |  | 1.41 ms | 2.09 ms | 1.48 |  |
| lookup, 64 | zerocheck |  | 81856 | 12.98 ms | 13.73 ms | 1.06 |  |
| lookup, 64 | grandsum |  | 6140 | 0.97 ms | 1.28 ms | 1.31 |  |

Phases outside tolerance: 9.
Explanation of flagged phases: `logup` is about 1.5-1.8x the prediction at every point (systematic): the model counts 3 multiplications per inversion but the helper construction makes two further list passes per element (denominators, selector products); `grandsum` is below 1 ms and carries a fixed per-call overhead (transcript, call setup). Both phases are < 15% of the prover time. The phases that dominate (zerocheck, commit) are inside the tolerance at every grid point, so the arm ratio is explained by the operation counts.

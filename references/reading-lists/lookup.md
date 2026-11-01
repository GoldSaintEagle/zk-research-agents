# Lookup arguments

Lookup and memory-checking arguments: offline memory checking (BEGKN), early lookup use in program-execution proofs (Arya), Plookup, sublinear-in-table KZG lookups (Caulk, Caulk+, flookup, cq, Baloo and successors, univariate sum-check lookups, CFFLL24, CFG25), sum-check / log-derivative style lookups for virtual machines (Lasso, Jolt, Twist and Shout), and folding of lookup instances (FLI). Entries partly drawn from Thaler's bibliography.

Suggested order: BEGKN94 [in zkvm] -> BCGJM18 (foundations); GW20 (Plookup); ZBKMNS22 -> PK22 -> GK22 -> EFG22 -> ZGKMR25 -> ZSG24 -> CFFLL24 -> CFG25 (KZG / table-independent line); Hab22 -> PH23 (log-derivative line); STW24 -> AST24 [in zkvm] -> STZ26 (sum-check / zkVM line); GM24 (folding lookups).

BibTeX: [`lookup.bib`](lookup.bib) — 15 entries, checked on 2026-11-01 with `skills/bib-verify/scripts/verify_bib.py`: 9 `VERIFIED` (title, authors, year) through Crossref / DataCite DOIs, 6 `VERIFIED (mirror)` — ePrint-only papers, matched against the third-party ePrint mirror because eprint.iacr.org refused this machine on that date. Re-check the mirror rows against eprint.iacr.org when it is reachable. ePrint rows link and cite the official `https://eprint.iacr.org/YYYY/NNNN`; the DOI / ePrint column links the version the entry was verified against. The venue column is informational and was not machine-checked. Re-run the verifier before copying entries into a paper.

Also part of this direction, listed once elsewhere to avoid duplicates (marked `[in …]` in the order above): `BEGKN94` Checking the correctness of memories ([zkvm](zkvm.md)); `AST24` Jolt: SNARKs for Virtual Machines via Lookups ([zkvm](zkvm.md)).

| key | DOI / ePrint | year | title | venue | why read |
|---|---|---|---|---|---|
| `BCGJM18` | [doi](https://doi.org/10.1007/978-3-030-03326-2_20) | 2018 | Arya: Nearly Linear-Time Zero-Knowledge Proofs for Correct Program Execution | ASIACRYPT 2018 | Arya: early lookup/permutation argument |
| `GW20` | [ePrint 2020/315](https://eprint.iacr.org/2020/315) | 2020 | plookup: A simplified polynomial protocol for lookup tables | ePrint | Plookup: the sorted-concatenation lookup used in Plonkish systems |
| `ZBKMNS22` | [doi](https://doi.org/10.1145/3548606.3560646) | 2022 | Caulk: Lookup Arguments in Sublinear Time | CCS 2022 | Caulk: first lookup sublinear in the table size |
| `PK22` | [ePrint 2022/957](https://eprint.iacr.org/2022/957) | 2022 | Caulk+: Table-independent lookup arguments | ePrint | Caulk+: prover independent of table size |
| `GK22` | [ePrint 2022/1447](https://eprint.iacr.org/2022/1447) | 2022 | flookup: Fractional decomposition-based lookups in quasi-linear time independent of table size | ePrint | flookup: fractional decomposition, table-independent |
| `Hab22` | [ePrint 2022/1530](https://eprint.iacr.org/2022/1530) | 2022 | Multivariate lookups based on logarithmic derivatives | ePrint | logUp: logarithmic-derivative lookups |
| `EFG22` | [ePrint 2022/1763](https://eprint.iacr.org/2022/1763) | 2022 | cq: Cached quotients for fast lookups | ePrint | cq: cached quotients, log-derivative lookup over KZG |
| `PH23` | [ePrint 2023/1284](https://eprint.iacr.org/2023/1284) | 2023 | Improving logarithmic derivative lookups using GKR | ePrint | logUp-GKR: log-derivative sums proven with GKR |
| `CFFLL24` | [doi](https://doi.org/10.1007/978-3-031-57722-2_11) | 2024 | Lookup Arguments: Improvements, Extensions and Applications to Zero-Knowledge Decision Trees | PKC 2024 | lookup improvements and extensions |
| `GM24` | [doi](https://doi.org/10.1007/978-981-96-0935-2_13) | 2024 | FLI: Folding Lookup Instances | ASIACRYPT 2024 | FLI: folding lookup instances |
| `STW24` | [doi](https://doi.org/10.1007/978-3-031-58751-1_7) | 2024 | Unlocking the Lookup Singularity with Lasso | EUROCRYPT 2024 | Lasso: sum-check lookups, structured tables |
| `ZSG24` | [doi](https://doi.org/10.1007/978-3-031-57722-2_13) | 2024 | Efficient KZG-Based Univariate Sum-Check and Lookup Argument | PKC 2024 | KZG univariate sum-check + lookup |
| `CFG25` | [doi](https://doi.org/10.1007/s00145-024-09535-0) | 2025 | Natively Compatible Super-Efficient Lookup Arguments and How to Apply Them | J. Cryptol. 2025 | super-efficient lookups, composition |
| `ZGKMR25` | [doi](https://doi.org/10.62056/ae890l5vt) | 2025 | Baloo: Algebraic Lookup Arguments | IACR Commun. Cryptol. 2025 | Baloo: table-size-independent lookups |
| `STZ26` | [doi](https://doi.org/10.1007/978-3-032-35424-2_10) | 2026 | Twist and Shout: Faster Memory Checking Arguments via One-Hot Addressing and Increments | CRYPTO 2026 | Twist and Shout: one-hot memory checking |

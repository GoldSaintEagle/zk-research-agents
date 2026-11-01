# Lookup arguments

Lookup and memory-checking arguments: offline memory checking (BEGKN), early lookup use in program-execution proofs (Arya), sublinear-in-table KZG lookups (Baloo and successors, univariate sum-check lookups, CFFLL24, CFG25), sum-check / log-derivative style lookups for virtual machines (Lasso, Jolt, Twist and Shout), and folding of lookup instances (FLI). Entries partly drawn from Thaler's bibliography.

Suggested order: BEGKN94 [in zkvm] -> BCGJM18 (foundations); ZGKMR25 -> ZSG24 -> CFFLL24 -> CFG25 (KZG / table-independent line); STW24 -> AST24 [in zkvm] -> STZ26 (sum-check / zkVM line); GM24 (folding lookups).

BibTeX: [`lookup.bib`](lookup.bib) — 8 entries, all VERIFIED (title, authors, year) on 2026-11-01 through Crossref / DataCite DOIs with `skills/bib-verify/scripts/verify_bib.py`; ePrint ids omitted because eprint.iacr.org refused this machine on that date — add `eprint=` after an ePrint-reachable re-run. The DOI column links the version the entry was verified against; the venue column is informational (from the Crossref container title) and was not machine-checked. Re-run the verifier before copying entries into a paper.

Also part of this direction, listed once elsewhere to avoid duplicates (marked `[in …]` in the order above): `BEGKN94` Checking the correctness of memories ([zkvm](zkvm.md)); `AST24` Jolt: SNARKs for Virtual Machines via Lookups ([zkvm](zkvm.md)).

| key | DOI | year | title | venue | why read |
|---|---|---|---|---|---|
| `BCGJM18` | [doi](https://doi.org/10.1007/978-3-030-03326-2_20) | 2018 | Arya: Nearly Linear-Time Zero-Knowledge Proofs for Correct Program Execution | ASIACRYPT 2018 | Arya: early lookup/permutation argument |
| `CFFLL24` | [doi](https://doi.org/10.1007/978-3-031-57722-2_11) | 2024 | Lookup Arguments: Improvements, Extensions and Applications to Zero-Knowledge Decision Trees | PKC 2024 | lookup improvements and extensions |
| `GM24` | [doi](https://doi.org/10.1007/978-981-96-0935-2_13) | 2024 | FLI: Folding Lookup Instances | ASIACRYPT 2024 | FLI: folding lookup instances |
| `STW24` | [doi](https://doi.org/10.1007/978-3-031-58751-1_7) | 2024 | Unlocking the Lookup Singularity with Lasso | EUROCRYPT 2024 | Lasso: sum-check lookups, structured tables |
| `ZSG24` | [doi](https://doi.org/10.1007/978-3-031-57722-2_13) | 2024 | Efficient KZG-Based Univariate Sum-Check and Lookup Argument | PKC 2024 | KZG univariate sum-check + lookup |
| `CFG25` | [doi](https://doi.org/10.1007/s00145-024-09535-0) | 2025 | Natively Compatible Super-Efficient Lookup Arguments and How to Apply Them | J. Cryptol. 2025 | super-efficient lookups, composition |
| `ZGKMR25` | [doi](https://doi.org/10.62056/ae890l5vt) | 2025 | Baloo: Algebraic Lookup Arguments | IACR Commun. Cryptol. 2025 | Baloo: table-size-independent lookups |
| `STZ26` | [doi](https://doi.org/10.1007/978-3-032-35424-2_10) | 2026 | Twist and Shout: Faster Memory Checking Arguments via One-Hot Addressing and Increments | CRYPTO 2026 | Twist and Shout: one-hot memory checking |

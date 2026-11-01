# IVC, PCD, accumulation and folding

Incremental verification and proof-carrying data: Valiant's IVC, SNARK recursion and bootstrapping (BCCT13) and its practical form over curve cycles (BCTV14), accumulation and split accumulation (BCMS20, BCLMS21), PCD from arithmetized random oracles, folding schemes (Nova, HyperNova, ProtoStar, NeutronNova, Nebula), hash- and lattice-based accumulation (Arc, linear-time accumulation, LatticeFold), and folding-based SNARK frameworks (Mangrove). Entries partly drawn from the bibliographic notes of [CY24 §Bibliographic notes, section:bibliographic-notes] and Thaler's bibliography.

Suggested order: Val08 -> BCCT13 -> BCTV14 (recursion line); BCMS20 -> BCLMS21 -> CCGOS23 (accumulation / PCD line); KST22 -> KS24 -> BC23 -> NDCTB24 -> KS26 -> AS26 [in zkvm] (folding line); BMNW25 -> BCFW25 -> BC25 (hash / lattice accumulation line).

BibTeX: [`folding-recursion.bib`](folding-recursion.bib) — 14 entries, all VERIFIED (title, authors, year) on 2026-11-01 through Crossref / DataCite DOIs with `skills/bib-verify/scripts/verify_bib.py`; ePrint ids omitted because eprint.iacr.org refused this machine on that date — add `eprint=` after an ePrint-reachable re-run. The DOI column links the version the entry was verified against; the venue column is informational (from the Crossref container title) and was not machine-checked. Re-run the verifier before copying entries into a paper.

Also part of this direction, listed once elsewhere to avoid duplicates (marked `[in …]` in the order above): `AS26` Nebula: Proving Machine Executions via Folding Schemes ([zkvm](zkvm.md)).

| key | DOI | year | title | venue | why read |
|---|---|---|---|---|---|
| `Val08` | [doi](https://doi.org/10.1007/978-3-540-78524-8_1) | 2008 | Incrementally Verifiable Computation or Proofs of Knowledge Imply Time/Space Efficiency | TCC 2008 | IVC definition |
| `BCCT13` | [doi](https://doi.org/10.1145/2488608.2488623) | 2013 | Recursive composition and bootstrapping for SNARKS and proof-carrying data | STOC 2013 | recursive SNARK composition, PCD |
| `BCTV14` | [doi](https://doi.org/10.1007/978-3-662-44381-1_16) | 2014 | Scalable Zero Knowledge via Cycles of Elliptic Curves | CRYPTO 2014 | recursion over curve cycles |
| `BCMS20` | [doi](https://doi.org/10.1007/978-3-030-64378-2_1) | 2020 | Recursive Proof Composition from Accumulation Schemes | TCC 2020 | accumulation schemes (Halo formalised) |
| `BCLMS21` | [doi](https://doi.org/10.1007/978-3-030-84242-0_24) | 2021 | Proof-Carrying Data Without Succinct Arguments | CRYPTO 2021 | split accumulation |
| `KST22` | [doi](https://doi.org/10.1007/978-3-031-15985-5_13) | 2022 | Nova: Recursive Zero-Knowledge Arguments from Folding Schemes | CRYPTO 2022 | Nova folding |
| `BC23` | [doi](https://doi.org/10.1007/978-981-99-8724-5_3) | 2023 | Protostar: Generic Efficient Accumulation/Folding for Special-Sound Protocols | ASIACRYPT 2023 | ProtoStar: folding special-sound protocols |
| `CCGOS23` | [doi](https://doi.org/10.1007/978-3-031-30617-4_13) | 2023 | Proof-Carrying Data from Arithmetized Random Oracles | EUROCRYPT 2023 | PCD in the (arithmetized) ROM |
| `KS24` | [doi](https://doi.org/10.1007/978-3-031-68403-6_11) | 2024 | HyperNova: Recursive Arguments for Customizable Constraint Systems | CRYPTO 2024 | HyperNova: folding CCS |
| `NDCTB24` | [doi](https://doi.org/10.1007/978-3-031-68403-6_10) | 2024 | Mangrove: A Scalable Framework for Folding-Based SNARKs | CRYPTO 2024 | Mangrove: folding-based SNARKs |
| `BC25` | [doi](https://doi.org/10.1007/978-981-95-5099-9_11) | 2025 | LatticeFold: A Lattice-Based Folding Scheme and Its Applications to Succinct Proof Systems | ASIACRYPT 2025 | LatticeFold: lattice folding |
| `BCFW25` | [doi](https://doi.org/10.1007/978-3-032-12287-2_13) | 2025 | Linear-Time Accumulation Schemes | TCC 2025 | linear-time accumulation |
| `BMNW25` | [doi](https://doi.org/10.1007/978-3-032-01907-3_5) | 2025 | Arc: Accumulation for Reed–Solomon Codes | CRYPTO 2025 | Arc: accumulation for RS codes |
| `KS26` | [doi](https://doi.org/10.1007/978-3-032-35424-2_18) | 2026 | NeutronNova: Group-Based Folding Done Right | CRYPTO 2026 | NeutronNova: group-based folding |

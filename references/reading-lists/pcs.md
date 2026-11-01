# Polynomial commitment schemes

Polynomial commitments as the cryptographic half of a PIOP-based SNARK: pairing-based KZG, its multi-point batching (BDFG20) and multilinear variants (PST, Zeromorph, Gemini, Mercury), discrete-log inner-product arguments (BCCGP, Bulletproofs, Hyrax, Dory) and groups of unknown order (DARK), hash-based Reed-Solomon proximity tests (FRI, DEEP-FRI, proximity gaps, STIR, WHIR), linear-code PCS (Ligero, tensor codes, Brakedown, BaseFold, Blaze), and batching/aggregation of openings for additive schemes (Halo Infinite). Entries partly drawn from the bibliographic notes of [CY24 §Bibliographic notes, section:bibliographic-notes] and Thaler's bibliography.

Suggested order: KZG10 -> PST13 -> BCHO22 -> KT24 -> EG25 (pairing / multilinear-from-univariate line); BCCGP16 -> BBBPWM18 -> WTSTW18 -> Lee21 -> BFS20 -> BDFG20 -> BDFG21 (inner-product / unknown-order / batching line); BBHR18fri -> BGKS20 [in fiat-shamir-soundness] -> BCIKS20 [in fiat-shamir-soundness] -> ACFY24 -> ACFY25 (RS proximity / IOPP line); AHIV23 -> BCG20 -> GLSTW23 -> ZCF24 -> BCFRRZ25 (linear-code PCS line).

BibTeX: [`pcs.bib`](pcs.bib) — 20 entries, checked on 2026-11-01 with `skills/bib-verify/scripts/verify_bib.py`: 18 `VERIFIED` (title, authors, year) through Crossref / DataCite DOIs, 2 `VERIFIED (mirror)` — ePrint-only papers, matched against the third-party ePrint mirror because eprint.iacr.org refused this machine on that date. Re-check the mirror rows against eprint.iacr.org when it is reachable. ePrint rows link and cite the official `https://eprint.iacr.org/YYYY/NNNN`; the DOI / ePrint column links the version the entry was verified against. The venue column is informational and was not machine-checked. Re-run the verifier before copying entries into a paper.

Also part of this direction, listed once elsewhere to avoid duplicates (marked `[in …]` in the order above): `BCIKS20` Proximity Gaps for Reed–Solomon Codes ([fiat-shamir-soundness](fiat-shamir-soundness.md)); `BGKS20` DEEP-FRI: Sampling Outside the Box Improves Soundness ([fiat-shamir-soundness](fiat-shamir-soundness.md)).

| key | DOI / ePrint | year | title | venue | why read |
|---|---|---|---|---|---|
| `KZG10` | [doi](https://doi.org/10.1007/978-3-642-17373-8_11) | 2010 | Constant-Size Commitments to Polynomials and Their Applications | ASIACRYPT 2010 | KZG: constant-size pairing PCS |
| `PST13` | [doi](https://doi.org/10.1007/978-3-642-36594-2_13) | 2013 | Signatures of Correct Computation | TCC 2013 | multilinear KZG (PST) |
| `BCCGP16` | [doi](https://doi.org/10.1007/978-3-662-49896-5_12) | 2016 | Efficient Zero-Knowledge Arguments for Arithmetic Circuits in the Discrete Log Setting | EUROCRYPT 2016 | recursive inner-product argument |
| `BBBPWM18` | [doi](https://doi.org/10.1109/sp.2018.00020) | 2018 | Bulletproofs: Short Proofs for Confidential Transactions and More | IEEE S&P 2018 | Bulletproofs IPA |
| `BBHR18fri` | [doi](https://doi.org/10.4230/LIPIcs.ICALP.2018.14) | 2018 | Fast Reed-Solomon Interactive Oracle Proofs of Proximity | ICALP 2018 | FRI |
| `WTSTW18` | [doi](https://doi.org/10.1109/sp.2018.00060) | 2018 | Doubly-Efficient zkSNARKs Without Trusted Setup | IEEE S&P 2018 | Hyrax: sqrt-size multilinear PCS |
| `BCG20` | [doi](https://doi.org/10.1007/978-3-030-64378-2_2) | 2020 | Linear-Time Arguments with Sublinear Verification from Tensor Codes | TCC 2020 | tensor-code PCS / linear-time prover |
| `BFS20` | [doi](https://doi.org/10.1007/978-3-030-45721-1_24) | 2020 | Transparent SNARKs from DARK Compilers | EUROCRYPT 2020 | DARK: PCS from groups of unknown order |
| `BDFG20` | [ePrint 2020/081](https://eprint.iacr.org/2020/081) | 2020 | Efficient polynomial commitment schemes for multiple points and polynomials | ePrint | batched KZG openings at many points (shplonk-style) |
| `BDFG21` | [doi](https://doi.org/10.1007/978-3-030-84242-0_23) | 2021 | Halo Infinite: Proof-Carrying Data from Additive Polynomial Commitments | CRYPTO 2021 | additive PCS, batching and PCD |
| `Lee21` | [doi](https://doi.org/10.1007/978-3-030-90453-1_1) | 2021 | Dory: Efficient, Transparent Arguments for Generalised Inner Products and Polynomial Commitments | TCC 2021 | Dory: transparent log-verifier PCS |
| `BCHO22` | [doi](https://doi.org/10.1007/978-3-031-07085-3_15) | 2022 | Gemini: Elastic SNARKs for Diverse Environments | EUROCRYPT 2022 | Gemini: multilinear from univariate |
| `AHIV23` | [doi](https://doi.org/10.1007/s10623-023-01222-8) | 2023 | Ligero: lightweight sublinear arguments without a trusted setup | Des. Codes Cryptogr. 2023 | Ligero (journal version) |
| `GLSTW23` | [doi](https://doi.org/10.1007/978-3-031-38545-2_7) | 2023 | Brakedown: Linear-Time and Field-Agnostic SNARKs for R1CS | CRYPTO 2023 | Brakedown: linear-code PCS |
| `ACFY24` | [doi](https://doi.org/10.1007/978-3-031-68403-6_12) | 2024 | STIR: Reed-Solomon Proximity Testing with Fewer Queries | CRYPTO 2024 | STIR: fewer-query RS IOPP |
| `KT24` | [doi](https://doi.org/10.1007/s00145-024-09519-0) | 2024 | Zeromorph: Zero-Knowledge Multilinear-Evaluation Proofs from Homomorphic Univariate Commitments | J. Cryptol. 2024 | Zeromorph: multilinear from KZG |
| `ZCF24` | [doi](https://doi.org/10.1007/978-3-031-68403-6_5) | 2024 | BaseFold: Efficient Field-Agnostic Polynomial Commitment Schemes from Foldable Codes | CRYPTO 2024 | BaseFold: foldable-code PCS |
| `ACFY25` | [doi](https://doi.org/10.1007/978-3-031-91134-7_8) | 2025 | WHIR: Reed–Solomon Proximity Testing with Super-Fast Verification | EUROCRYPT 2025 | WHIR: multilinear RS PCS, fast verifier |
| `BCFRRZ25` | [doi](https://doi.org/10.1007/978-3-031-91134-7_5) | 2025 | Blaze: Fast SNARKs from Interleaved RAA Codes | EUROCRYPT 2025 | Blaze: RAA-code PCS |
| `EG25` | [ePrint 2025/385](https://eprint.iacr.org/2025/385) | 2025 | MERCURY: A multilinear Polynomial Commitment Scheme with constant proof size and no prover FFTs | ePrint | Mercury: constant-size multilinear PCS from KZG, no FFTs |

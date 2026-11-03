# Fiat-Shamir and concrete soundness

The Fiat-Shamir transform and what it takes to make it sound: the forking lemma (Pointcheval-Stern, Bellare-Neven), the random-oracle caveats (CGH, Goldwasser-Kalai), Micali's CS proofs and the BCS IOP compiler with state-restoration soundness, round-by-round soundness (and its relation to state restoration, Hol19) and correlation intractability (CCRR18, CCHLRR19, PS19), the multi-round special-soundness analysis (AFK22), tight bounds for Micali/BCS (CY21) and FRI-based SNARKs (BGKTTZ23, BGTZ25), the proximity-gap and DEEP results that fix FRI's concrete soundness (BGKS20, BCIKS20), the duplex-sponge instantiation (CO25), and the attacks that show what goes wrong in practice (weak Fiat-Shamir: BPW12, DMWG23; a practical attack on a sound-in-theory instantiation: KRS25). Entries partly drawn from the bibliographic notes of [CY24 §Bibliographic notes, section:bibliographic-notes]. Holmgren's note on round-by-round soundness vs. state-restoration attacks is ePrint-only and left out.

Suggested order: FS86 -> PS00 -> BN06 (transform, forking); CGH04 -> GK03 (random-oracle caveats); BPW12 -> DMWG23 -> KRS25 (attacks); Mic00 -> BCS16 [in piop-arithmetization] -> CY21 (compilers, state-restoration soundness); CCRR18 -> CCHLRR19 -> PS19 -> Hol19 (correlation intractability, round-by-round); AFK22 (multi-round special soundness); BGKS20 -> BCIKS20 -> BGKTTZ23 -> BGTZ25 (FRI/IOP concrete soundness); CO25 (sponge instantiation).

BibTeX: [`fiat-shamir-soundness.bib`](fiat-shamir-soundness.bib) — 20 entries, checked on 2026-11-01 with `skills/bib-verify/scripts/verify_bib.py`: 19 `VERIFIED` (title, authors, year) through Crossref / DataCite DOIs, 1 ePrint-only papers matched first against the third-party ePrint mirror (eprint.iacr.org refused this machine on that date) and re-checked on 2026-11-03 against eprint.iacr.org itself with `--require-official`: `VERIFIED`. ePrint rows link and cite the official `https://eprint.iacr.org/YYYY/NNNN`; the DOI / ePrint column links the version the entry was verified against. The venue column is informational and was not machine-checked. Re-run the verifier before copying entries into a paper.

Also part of this direction, listed once elsewhere to avoid duplicates (marked `[in …]` in the order above): `BCS16` Interactive Oracle Proofs ([piop-arithmetization](piop-arithmetization.md)).

| key | DOI / ePrint | year | title | venue | why read |
|---|---|---|---|---|---|
| `FS86` | [doi](https://doi.org/10.1007/3-540-47721-7_12) | 1986 | How To Prove Yourself: Practical Solutions to Identification and Signature Problems | CRYPTO 1986 | Fiat-Shamir |
| `PS00` | [doi](https://doi.org/10.1007/s001450010003) | 2000 | Security Arguments for Digital Signatures and Blind Signatures | J. Cryptology 2000 | forking lemma (full version) |
| `Mic00` | [doi](https://doi.org/10.1137/s0097539795284959) | 2000 | Computationally Sound Proofs | SIAM J. Comput. 2000 | Micali's PCP-to-SNARG compiler |
| `GK03` | [doi](https://doi.org/10.1109/sfcs.2003.1238185) | 2003 | On the (In)security of the Fiat-Shamir paradigm | FOCS 2003 | uninstantiable FS |
| `CGH04` | [doi](https://doi.org/10.1145/1008731.1008734) | 2004 | The random oracle methodology, revisited | J. ACM 2004 | ROM separation |
| `BN06` | [doi](https://doi.org/10.1145/1180405.1180453) | 2006 | Multi-signatures in the plain public-Key model and a general forking lemma | CCS 2006 | general forking lemma |
| `BPW12` | [doi](https://doi.org/10.1007/978-3-642-34961-4_38) | 2012 | How Not to Prove Yourself: Pitfalls of the Fiat-Shamir Heuristic and Applications to Helios | ASIACRYPT 2012 | weak vs. strong FS |
| `CCRR18` | [doi](https://doi.org/10.1007/978-3-319-78381-9_4) | 2018 | Fiat-Shamir and Correlation Intractability from Strong KDM-Secure Encryption | EUROCRYPT 2018 | correlation intractability |
| `CCHLRR19` | [doi](https://doi.org/10.1145/3313276.3316380) | 2019 | Fiat-Shamir: from practice to theory | STOC 2019 | round-by-round soundness |
| `PS19` | [doi](https://doi.org/10.1007/978-3-030-26948-7_4) | 2019 | Noninteractive Zero Knowledge for NP from (Plain) Learning with Errors | CRYPTO 2019 | sound FS from LWE |
| `Hol19` | [ePrint 2019/1261](https://eprint.iacr.org/2019/1261) | 2019 | On Round-By-Round Soundness and State Restoration Attacks | ePrint | RBR vs state-restoration soundness |
| `BGKS20` | [doi](https://doi.org/10.4230/LIPIcs.ITCS.2020.5) | 2020 | DEEP-FRI: Sampling Outside the Box Improves Soundness | ITCS 2020 | DEEP, FRI soundness |
| `BCIKS20` | [doi](https://doi.org/10.1109/focs46700.2020.00088) | 2020 | Proximity Gaps for Reed-Solomon Codes | FOCS 2020 (J. ACM 2023) | proximity gaps, FRI bounds |
| `CY21` | [doi](https://doi.org/10.1007/978-3-030-90459-3_14) | 2021 | Tight Security Bounds for Micali's SNARGs | TCC 2021 | tight ROM bounds |
| `AFK22` | [doi](https://doi.org/10.1007/978-3-031-22318-1_5) | 2022 | Fiat-Shamir Transformation of Multi-round Interactive Proofs | TCC 2022 (J. Cryptology 2023) | multi-round special soundness |
| `DMWG23` | [doi](https://doi.org/10.1109/sp46215.2023.10179408) | 2023 | Weak Fiat-Shamir Attacks on Modern Proof Systems | IEEE S&P 2023 | transcript-hashing bugs in deployed SNARKs |
| `BGKTTZ23` | [doi](https://doi.org/10.1007/978-981-99-8724-5_1) | 2023 | Fiat-Shamir Security of FRI and Related SNARKs | ASIACRYPT 2023 | round-by-round for FRI |
| `BGTZ25` | [doi](https://doi.org/10.1007/s00145-024-09520-7) | 2025 | On Soundness Notions for Interactive Oracle Proofs | J. Cryptology 2025 | IOP soundness notions compared |
| `KRS25` | [doi](https://doi.org/10.1007/978-3-032-01887-8_1) | 2025 | How to Prove False Statements: Practical Attacks on Fiat-Shamir | CRYPTO 2025 | attack on FS with a concrete hash |
| `CO25` | [doi](https://doi.org/10.1007/978-3-032-12287-2_16) | 2025 | A Fiat-Shamir Transformation from Duplex Sponges | TCC 2025 | sponge-based FS |

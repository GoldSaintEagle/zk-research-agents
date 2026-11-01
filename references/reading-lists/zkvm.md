# zkVMs and VM/CPU arithmetization

Proving the execution of a whole machine rather than a fixed circuit: offline memory checking (Blum et al.), the RAM-to-constraint reductions and TinyRAM/vnTinyRAM line (BCGT13, SNARKs for C, cycles of curves), stateful verifiable computation (Pantry, Buffet, vRAM), RAM-model ZK outside SNARKs (Arya, Hu-Mohassel-Rosulek, constant-overhead ZK for RAM), incremental verification as the basis of continuations/segmentation (Valiant's IVC, Nebula, Ceno's segment-wise proving), and the lookup-centric zkVM design (Jolt, with Twist and Shout as its memory-checking argument). Lasso is cited from the lookup list, not here. Cairo, the RISC Zero and SP1 write-ups, Spice (OSDI 2018) and the vnTinyRAM USENIX Security 2014 paper are left out because no DOI could be verified for them.

Suggested order: BEGKN94 -> BCGT13 -> BCGTV13 -> BCTV14 [in folding-recursion] (RAM reductions, TinyRAM); BFRSBW13 -> WSRBW15 -> ZGKPP18 (stateful verifiable computation, memory); HMR15 -> MRS17 -> BCGJM18 [in lookup] -> FKLOWW21 (RAM-model ZK); Val08 [in folding-recursion] -> AS26 -> LZZHZ25 (incremental / segmented proving, continuations); AST24 -> STZ26 [in lookup] (lookup-based zkVM, memory checking).

BibTeX: [`zkvm.bib`](zkvm.bib) — 12 entries, verified on 2026-11-01 through Crossref / DataCite DOIs with skills/bib-verify/scripts/verify_bib.py; ePrint ids omitted because eprint.iacr.org refused this machine on that date — add `eprint=` after an ePrint-reachable re-run. The venue column is informational and was not machine-checked. Re-run the verifier before copying entries into a paper.

Also part of this direction, listed once elsewhere to avoid duplicates (marked `[in …]` in the order above): `BCGJM18` Arya: Nearly Linear-Time Zero-Knowledge Proofs for Correct Program Execution ([lookup](lookup.md)); `STZ26` Twist and Shout: Faster Memory Checking Arguments via One-Hot Addressing and Increments ([lookup](lookup.md)); `Val08` Incrementally Verifiable Computation or Proofs of Knowledge Imply Time/Space Efficiency ([folding-recursion](folding-recursion.md)); `BCTV14` Scalable Zero Knowledge via Cycles of Elliptic Curves ([folding-recursion](folding-recursion.md)).

| key | DOI | year | title | venue | why read |
|---|---|---|---|---|---|
| `BEGKN94` | [doi](https://doi.org/10.1007/bf01185212) | 1994 | Checking the correctness of memories | Algorithmica 1994 (FOCS 1991) | offline memory checking |
| `BCGT13` | [doi](https://doi.org/10.1145/2422436.2422481) | 2013 | Fast reductions from RAMs to delegatable succinct constraint satisfaction problems | ITCS 2013 | RAM-to-constraint reduction |
| `BCGTV13` | [doi](https://doi.org/10.1007/978-3-642-40084-1_6) | 2013 | SNARKs for C: Verifying Program Executions Succinctly and in Zero Knowledge | CRYPTO 2013 | TinyRAM, routing-based memory |
| `BFRSBW13` | [doi](https://doi.org/10.1145/2517349.2522733) | 2013 | Verifying computations with state | SOSP 2013 | Pantry, Merkle-backed RAM |
| `WSRBW15` | [doi](https://doi.org/10.14722/ndss.2015.23097) | 2015 | Efficient RAM and Control Flow in Verifiable Outsourced Computation | NDSS 2015 | Buffet, permutation-based memory |
| `HMR15` | [doi](https://doi.org/10.1007/978-3-662-48000-7_8) | 2015 | Efficient Zero-Knowledge Proofs of Non-algebraic Statements with Sublinear Amortized Cost | CRYPTO 2015 | ORAM-based ZK for RAM |
| `MRS17` | [doi](https://doi.org/10.1007/978-3-319-56620-7_18) | 2017 | Sublinear Zero-Knowledge Arguments for RAM Programs | EUROCRYPT 2017 | sublinear RAM ZK |
| `ZGKPP18` | [doi](https://doi.org/10.1109/sp.2018.00013) | 2018 | vRAM: Faster Verifiable RAM with Program-Independent Preprocessing | IEEE S&P 2018 | program-independent RAM |
| `FKLOWW21` | [doi](https://doi.org/10.1145/3460120.3484800) | 2021 | Constant-Overhead Zero-Knowledge for RAM Programs | CCS 2021 | VOLE-based RAM ZK |
| `AST24` | [doi](https://doi.org/10.1007/978-3-031-58751-1_1) | 2024 | Jolt: SNARKs for Virtual Machines via Lookups | EUROCRYPT 2024 | lookup-centric RISC-V zkVM |
| `LZZHZ25` | [doi](https://doi.org/10.1007/s00145-024-09533-2) | 2025 | Ceno: Non-uniform, Segment and Parallel Zero-Knowledge Virtual Machine | J. Cryptology 2025 | segment-wise, non-uniform zkVM |
| `AS26` | [doi](https://doi.org/10.1109/sp63933.2026.00099) | 2026 | Nebula: Proving Machine Executions via Folding Schemes | IEEE S&P 2026 | folding-based machine proving |

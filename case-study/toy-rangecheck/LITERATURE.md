# LITERATURE — related-work matrix (owner: `lit-scout`)

Format and column rules: `skills/lit-matrix/SKILL.md`; lint with `skills/lit-matrix/scripts/lit_matrix.py`
(log: `results/novelty/lit_matrix.log`). Sources: `references/reading-lists/lookup.md`,
`piop-arithmetization.md`, `circuit-security.md`, `fiat-shamir-soundness.md`; every row re-verified into
`bib-verify-report.md` on 2026-11-02. No concrete numbers are copied from the papers: this toy compares
encodings on its own backend only (DECISIONS D-1), so the "concrete numbers" column is `n/a`.

## Related-work matrix

| work | venue/year | arithmetization | pcs | setup | assumptions/model | pq? | field | p/v/π asymptotics | concrete numbers + source | code? | our delta |
|---|---|---|---|---|---|---|---|---|---|---|---|
| **plookup** [@GW20] | ePrint 2020 | Plonkish + lookup (sorted concatenation, grand product) | KZG (via PLONK) | universal | AGM + q-DLOG, ROM | no | pairing scalar field | prover O((n + T) log), table padded into the trace | n/a | unknown | we use logUp, not plookup; we measure the table-height floor on a toy backend |
| **logUp** [@Hab22] | ePrint 2022 | multivariate lookups via logarithmic derivatives, sum-check | multilinear PCS (any) | n/a | ROM; Schwartz–Zippel over the rational identity | n/a | any large field | prover O(n + T) field ops + helper columns | n/a | unknown | our lookup arm implements the logUp identity in a toy sum-check prover |
| **cq** [@EFG22] | ePrint 2022 | log-derivative lookup with cached quotients | KZG | universal | AGM, ROM | no | pairing scalar field | prover O(n log n) independent of T after preprocessing | n/a | unknown | table-independent prover; our toy pays for the whole table every proof |
| **Lasso** [@STW24] | EUROCRYPT 2024 | sum-check lookups into structured (decomposable) tables | multilinear PCS | n/a | ROM | n/a | large field | prover pays per lookup, not per table entry, for decomposable tables | n/a | unknown | we use a small unstructured table [0, 2^c) |
| logUp-GKR [@PH23] | ePrint 2023 | logUp with the fractional sums proven by GKR | multilinear PCS | n/a | ROM | n/a | large field | fewer committed helper columns than logUp | n/a | unknown | we commit every helper column (simpler, slower) |
| Caulk [@ZBKMNS22] | CCS 2022 | KZG lookup sublinear in table size | KZG | trusted | AGM, q-SBDH | no | pairing scalar field | prover sublinear in T | n/a | unknown | not a range-check study; cited for the sublinear-table line |
| Arya [@BCGJM18] | ASIACRYPT 2018 | early lookup / permutation argument for program execution | n/a | n/a | n/a | n/a | large field | n/a | n/a | unknown | historical: lookups in arithmetization |
| PLONK [@GWC19] | ePrint 2019 | Plonkish gates + permutation (copy constraints) | KZG | universal | AGM, ROM | no | pairing scalar field | prover O(n log n) | n/a | unknown | our arms are Plonkish tables in its sense |
| HyperPlonk [@CBBZ23] | EUROCRYPT 2023 | Plonkish over the boolean hypercube, sum-check zero-check | multilinear PCS | universal | ROM | n/a | large field | linear-time prover, high-degree gates | n/a | unknown | our toy prover is a stripped-down HyperPlonk-style zero-check (no PCS, no permutation argument) |
| Spartan [@Set20] | CRYPTO 2020 | R1CS via sum-check | multilinear PCS | transparent | ROM | n/a | large field | prover O(nnz) | n/a | unknown | our R1CS arm is counted, not proven |
| Sum-check [@LFKN92] | J. ACM 1992 | sum-check protocol | n/a | n/a | information-theoretic | yes (statistical) | any field | v rounds, degree-d messages | n/a | no | we use the toy sum-check of lib/cryptomath |
| IOPs / BCS [@BCS16] | TCC 2016-B | IOP → SNARG compiler (Merkle + FS) | Merkle | transparent | ROM | plausible: ROM / hash-based | any | — | n/a | no | our toy commits columns with Merkle roots in a FS transcript |
| FS pitfalls [@BPW12] | ASIACRYPT 2012 | weak vs strong Fiat–Shamir | n/a | n/a | ROM | n/a | n/a | n/a | n/a | no | our FS audit checks the statement binding of every sub-transcript |
| Picus [@PCWRVMCG23] | PLDI 2023 | under-constrained circuit detection (uniqueness via SMT) | n/a | n/a | n/a | n/a | any | n/a | n/a | yes https://github.com/Veridise/Picus | our audit is exhaustive over a small field, not SMT |
| ZK circuit verification [@CMS23] | EPTCS 2023 | formal verification of circuits | n/a | n/a | n/a | n/a | any | n/a | n/a | unknown | we only test small parameters |
| Circuit bug study [@WSCFPCDF23] | ePrint 2023 | taxonomy of ZK circuit bugs (under-constrained, missing range checks) | n/a | n/a | n/a | n/a | any | n/a | n/a | unknown | our planted bug is one of its classes (missing range constraint) |

Strongest baseline: bit decomposition with booleanity / a running-sum gate, the textbook encoding
([Thaler §6.5.4, Details of the Transformation]); lookup-based range checks: [Thaler §6.6.3, Efficiently Representing Non-Arithmetic Operations Over Large Prime-Order Fields].
True competitors (bold): plookup, logUp, cq, Lasso.

## Reading notes (competitors)

- **plookup [@GW20]** — the table is a fixed column of the trace; the lookup adds a sorted vector and a grand
  product. *Relevant to us:* the table occupies trace rows, so a 2^c table forces height ≥ 2^c — the effect the
  falsifier later measures at small k.
- **logUp [@Hab22]** — replaces the grand product by a sum of fractions 1/(β − f_i) = Σ m_j/(β − t_j) with
  multiplicities m_j; fits sum-check (multilinear) provers. *Relevant:* our lookup arm; costs helper columns for
  the fractions and the multiplicity column.
- **cq [@EFG22]** — log-derivative lookup whose prover work after preprocessing does not depend on the table
  size. *Relevant:* a real system would not pay our table-height floor; we state this as a limitation.
- **Lasso [@STW24]** — lookups into huge decomposable tables by sum-check, paying per lookup. *Relevant:* a
  64-bit range check could be one decomposable lookup; out of scope (D-1).

## Baseline candidates and code status
| candidate | code | status |
|---|---|---|
| running-sum bit decomposition (ours, same backend) | circuits/range_gadgets.py | chosen (D-4) |
| halo2 lookup range-check gadgets | public repositories (not pinned) | out of scope (D-1) |
| plonky3 / logUp-GKR implementations | public repositories (not pinned) | out of scope (D-1) |

## Novelty checks

- 2026-11-02 | query: "lookup range check" | sources: eprint | window: 12m | hits reviewed: 7 | verdict: overlap:Hab22

(Log: `results/novelty/eprint_lookup_range_check.md`. None of the 7 hits compares the two encodings on a toy
backend; the trade-off itself is textbook material — Thaler §6.6.3 and the lookup papers above — hence the
waived novelty items, DECISIONS D-2. Grey literature was not searched.)

## Pre-emption watch (ePrint + grey literature, last 12 months)
| date checked | query | hits | threat level | note |
|---|---|---|---|---|
| 2026-11-02 | lookup range check | 7 | none | teaching example; folklore trade-off |

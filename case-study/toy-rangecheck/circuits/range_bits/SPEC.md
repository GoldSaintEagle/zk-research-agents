# SPEC — range_bits (written before the constraints; owner: circuit-engineer)

Field F_p, parameters n ≥ 1, k ≥ 1 with **2^k < p** (k ≤ 63 in Goldilocks).

- Public input: x_1, …, x_n ∈ F_p.
- Relation: a witness exists **iff** every x_j, read as an integer in [0, p), satisfies x_j < 2^k.
- Uniqueness: for every accepted public input the witness (all `acc` cells; the bits b_i of R1CS) is unique.
- Intermediate values defined by the spec: acc_i = ⌊x / 2^(k-i)⌋ (MSB-first prefix of the bits), i = 0..k.
- Hints: none (every cell is determined).
- Encodings: `plonk_bits` (running-sum gate, Plonkish) and `r1cs_bits` (booleanity + recomposition).
- Outside 2^k < p (k = 64 in Goldilocks) the spec does not apply: the decomposition is not unique there
  ([Thaler §6.5.4, Details of the Transformation]; skills/circuit-audit item 6).

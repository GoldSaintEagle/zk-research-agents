# SPEC — range_lookup (written before the constraints; owner: circuit-engineer)

Field F_p, parameters n ≥ 1, k ≥ 1, limb width c ≥ 1, L = ⌈k/c⌉ limbs, r = k mod c; require 2^k < p and
2^(2c) < p (no wrap-around in the limb checks).

- Public input: x_1, …, x_n ∈ F_p.
- Relation: a witness exists **iff** every x_j < 2^k (as an integer in [0, p)).
- Uniqueness: for every accepted public input the witness (`acc` and `limb` cells) is unique.
- Intermediate values: limbs ℓ_0..ℓ_{L-1} = base-2^c digits of x, most significant first; acc_0 = 0,
  acc_{i+1} = 2^c·acc_i + ℓ_i, acc_L = x.
- Constraints required by this spec:
  1. acc_0 = 0;
  2. acc_{i+1} = 2^c·acc_i + ℓ_i for i < L;
  3. every limb ℓ_i ∈ [0, 2^c) by a lookup into the **fixed** table [0, 2^c);
  4. **if r ≠ 0, the top limb ℓ_0 < 2^r** (e.g. a second lookup of 2^(c−r)·ℓ_0 into the same table);
  5. acc_L copied to the public x_j.
- Hints: none (every cell is determined).
- Lookup argument: logUp (source: other, ePrint 2022/1530) in the toy prover (impl/).

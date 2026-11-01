# cryptomath

Readable, toy-scale mathematics for **screening zero-knowledge proof research**:
check an algebraic fact, run a tiny proof system end to end, measure a soundness
error empirically, or count the operations of a candidate prover before writing
it. The code is built to be correct and readable, not fast.

> **Everything in `zk/`, `protocols/` and `ec/` is insecure.** Fields are tiny,
> the RNG is not cryptographic, nothing is constant time, there is no
> zero-knowledge, and `zk/kzg.py` uses a *simulated* group whose discrete logs
> are public, so it is not even binding. These files start with
> `# TOY: not secure`. Never use them to protect data. A number from here goes
> into a paper only after it has been re-derived with a real tool (the
> compiler, the prover, Sage) and given an EVIDENCE row.

## Install / test

```bash
cd lib/cryptomath
pip install -e .                 # optional; the tests also run without installing
python3 -m pytest -q tests       # or: python3 -m unittest discover -s tests
```

Dependencies: Python ≥ 3.10, numpy, sympy (matplotlib optional). Sage is
optional and its imports are guarded.

`import cryptomath` loads subpackages lazily, and so does `cryptomath.zk`. If
a subpackage is missing or broken, the rest still works, and
`cryptomath.available()` reports which subpackages import cleanly.
`zk.{r1cs, plonkish, mle, sumcheck, merkle}` and `costmodel.{counter, zkops}`
need neither numpy nor sympy, so the skill scripts can use them from a bare
Python. The Fiat–Shamir and hiding variants import `protocols`, which needs
sympy, and they do so only when called.

## Module map

| subpackage | modules | what you get |
|---|---|---|
| `algebra` | `ntheory` | factorisation, φ, λ, multiplicative order, primitive roots, (Z/m)^* subgroups and cosets, NTT-friendly primes, roots of unity |
| | `poly` | list-polynomial arithmetic over Z and Z_q, Φ_m, `PolyRing` = Z_q[X]/f |
| | `finite_field` | GF(p^k) with the Rabin irreducibility test, minimal polynomials (extension fields for challenges) |
| | `ntt` | radix-2 cyclic and negacyclic NTT (counts butterflies), Bluestein DFT for any length, `CyclotomicNTT` |
| `zk` (TOY) | `field` | F_17, F_97, Goldilocks; inverses, batch inversion, roots of unity, Lagrange interpolation |
| | `mle` | multilinear extensions: evaluation by folding, `eq(x, r)` and its table |
| | `sumcheck` | sum-check prover and verifier (interactive and Fiat–Shamir), a cheating prover for measuring the v·d/p bound |
| | `merkle` | Merkle commitments, single and pruned multi-openings, collision extraction (the binding reduction), optional salted leaves |
| | `fri` | toy FRI with folding factor, rate and query count; exact proof-size count |
| | `kzg` | KZG **algebra only**, in a simulated group with known discrete logs (forgery demo included) |
| | `plonk` | PLONK grand-product permutation check from copy constraints; logUp lookup check |
| | `r1cs` | R1CS representation, satisfiability, failing-constraint report, counts, sparse matrices |
| | `plonkish` | Plonkish tables (gates, copies, lookups), satisfiability, row/column/degree counts |
| `costmodel` | `counter`, `traced` | `Counter` context, `count` / `counted` hooks, ZK op names (`msm`, `ntt_butterfly`, `hash`, `sumcheck_term`, ...), `Traced` values that count nonlinear multiplications (= R1CS constraints) and depth |
| | `zkops` | integer counts and `count_*` hooks: MSM (Pippenger), NTT, Merkle commit/open/pruned, sum-check, KZG commit/open/verify, FRI commit/fold/query |
| | `formulas` | sympy `CostFormula` (evaluate, weight, crossover), `compare()` report, and the symbolic twins of every `zkops` count |
| `symmetric` | `afcost` | cost formulas for arithmetisation-oriented primitives (MiMC, HADES/Poseidon, Rasta, LowMC, Trivium-like, AES): S-boxes, multiplications, depth |
| | `gf2n` | GF(2^n) arithmetic, power maps, Gold / Kasami exponents (binary-field proof systems) |
| `protocols` | `commitments` | hash commitment, Pedersen commitment (homomorphic) |
| | `fiat_shamir` | `Transcript` (labelled, length-prefixed, ratcheting), Schnorr sigma protocol with NIZK, HVZK simulator and special-soundness extractor |
| `ec` | `curve`, `groups`, `dlp` | small elliptic curves over GF(p), one interface over `ModPGroup` / `ZpStarGroup` / `ECGroup`, BSGS / Pollard rho / Pohlig–Hellman |

Skill scripts that build on this library: `skills/constraint-cost/scripts/constraint_count.py`
(`zk.r1cs`, `zk.plonkish`, `symmetric.afcost`), `skills/circuit-audit/scripts/toy_circuit_audit.py`
(`zk.r1cs`) and `skills/prover-cost-model/scripts/prover_cost_model.py` (`costmodel.zkops`; its
self-test runs `algebra.ntt` and `zk.sumcheck`).

## Quick examples

```python
import random
from cryptomath.zk import sumcheck, mle, merkle, fri
from cryptomath.costmodel import Counter, sumcheck_terms, sumcheck_formula

# sum-check over F_97: honest run, then the cheating prover's success rate vs the v*d/p bound
rng, p = random.Random(1), 97
tabs = [[rng.randrange(p) for _ in range(8)] for _ in range(2)]       # v = 3, d = 2
with Counter() as c:
    assert sumcheck.run(tabs, p, rng)["accepted"]
c["sumcheck_term"] == sumcheck_terms(3, 2) == sumcheck_formula().evaluate(v=3, d=2)["sumcheck_term"]
wins = sum(sumcheck.run(tabs, p, rng, sumcheck.CheatingProver(tabs, p, rng=rng))["accepted"]
           for _ in range(2000))
wins / 2000, sumcheck.soundness_bound(3, 2, p)    # ~0.06: exact 1-(1-d/p)^v = 0.061, bound v*d/p = 0.062

# Merkle: a pruned multi-opening is smaller than separate paths
T = merkle.MerkleTree([bytes([i]) for i in range(16)])
merkle.proof_size(4, {0, 1, 2, 3}), merkle.proof_size(4, {0, 1, 2, 3}, pruned=False)   # 64 vs 512 bytes

# FRI over F_97: degree < 8, blowup 4, 6 queries
prm = fri.FRIParams(N=8, fold=2, blowup=4, queries=6)
pf = fri.prove(fri.evaluate_on_domain(list(range(8)), prm.n0, p), prm, p)
fri.verify(pf, prm, p), fri.proof_size(prm, p)["total"]

# count a gadget's constraints before writing it in a circuit DSL
from cryptomath.costmodel import Traced
with Counter() as g:
    x = Traced(3)
    y = x ** 5 + 7 * x                 # Poseidon-style S-box plus a linear term
g["mult"], y.depth                     # 3 constraints, depth 3
```

Screening workflow: write the new idea and the baseline as plain Python
functions over abstract operations, `count_*` hooks or `Traced` values. Then
`compare(new, baseline, *args)` checks that the outputs agree and prints a
Markdown table of op counts and weighted cost. Only ideas that pass this
screen get a real implementation (`impl/`, `circuits/`).

## Conventions

* Field elements are Python ints in [0, p). Polynomials are coefficient lists,
  lowest degree first.
* Multilinear tables: variable x_1 is the most significant bit of the index, so
  binding x_1 splits a table into its low and high halves.
* Merkle trees are binary over a power-of-two number of leaves; leaf hash
  H(0x00 ‖ data), node hash H(0x01 ‖ left ‖ right), SHA-256 truncated to
  `hash_bytes`.
* Module docstrings cite the two reference books (Thaler; Chiesa–Yogev, CY24) in the
  format of `references/books/README.md`, checked by `scripts/check_book_refs.py`,
  and other public sources by author, year and ePrint number.

## References (public)

Each module docstring lists its references. Besides the two reference books:
PLONK (ePrint 2019/953); logUp (ePrint 2022/1530); MiMC (ePrint 2016/492);
Poseidon (ePrint 2019/458); HADES (ePrint 2019/1107); Rasta (ePrint 2018/181);
Pedersen, CRYPTO 1991; Schnorr, J. Cryptology 1991; Fiat–Shamir, CRYPTO 1986;
Shanks 1971; Pollard 1978; Pohlig–Hellman 1978.

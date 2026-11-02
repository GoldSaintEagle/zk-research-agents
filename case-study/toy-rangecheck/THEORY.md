# THEORY — statements, proof status, formalisation (owner: `theorist`)

Toy protocol, toy parameters: everything below is for teaching; the parameters are insecure by design.

| paper label | statement (short) | notion and model | proof status (sketch/full/checked) | numeric check (script) | Lean name | sorry-free? |
|---|---|---|---|---|---|---|
| L1 | running-sum bit decomposition accepts exactly [0, 2^k), unique witness, if 2^k < p | relation equality (circuit vs SPEC) | full (below) | theory/check_gadgets.py L1 (722 cases, PASS) | — | — |
| L2 | limbs in [0, 2^c) by lookup + top-limb check + recomposition accept exactly [0, 2^k), unique, if 2^k < p and 2^(2c) < p; without the top-limb check (r ≠ 0) the accepted set is [0, 2^(cL)) | relation equality | full (below) | L2 (682 cases), L2n (3 cases) PASS | — | — |
| L3 | if 2^k > p, every x < 2^k − p has two witnesses (both encodings): k = 64 in Goldilocks is not a range check | relation | full | L3 (23 cases) PASS | — | — |
| L4 | logUp: a wrong lookup satisfies the identity for at most M + T − 1 challenges | Schwartz–Zippel on the cleared rational identity | full (MATH-REFS M6) | L4 (6480 cases over F_17) PASS | — | — |
| T1 | the toy argument (impl/) is sound for the range-check relation of L1/L2 with error ε(t) of the budget below | soundness (not knowledge soundness), ROM, transparent; verifier with oracle access to the committed columns (TOY) | sketch (below) | budget: theory/budget.py → results/soundness/ | — | — |

Lean: not used (lean/ empty); the lemmas are finite statements checked exhaustively on small fields and proved
by hand below. Lower bound: none known for the toy beyond the tightness of Schwartz–Zippel (the cheating
sum-check prover of lib/cryptomath meets v·d/p up to second-order terms).

## Proofs (hand)

**L1.** Gate `zero` forces acc_0 = 0; `runsum` forces d_i = acc_{i+1} − 2acc_i ∈ {0, 1} (a degree-2 polynomial
with roots 0, 1 in a field). So acc_k = Σ 2^(k−1−i) d_i mod p. The integer value lies in [0, 2^k); if 2^k < p it is
already reduced, so acc_k = x forces x < 2^k and the d_i are its binary digits (unique), hence every acc_i is
unique. Conversely the binary digits of x < 2^k satisfy every gate. [Thaler §6.5.4, Details of the Transformation].

**L2.** Lookups force ℓ_i ∈ [0, 2^c). If r ≠ 0, the second lookup forces 2^(c−r)ℓ_0 mod p ∈ [0, 2^c); since
ℓ_0 < 2^c and 2^(2c−r) < p there is no reduction, so ℓ_0 < 2^r. Then Σ 2^(c(L−1−i)) ℓ_i < 2^k < p: no reduction,
recomposition gives x < 2^k with unique base-2^c digits. Without the second lookup only ℓ_0 < 2^c holds and the
accepted set is [0, 2^(cL)) ∩ [0, p) — strictly larger when r ≠ 0 (L2n). [Thaler §6.6.3, Efficiently Representing Non-Arithmetic Operations Over Large Prime-Order Fields].

**L3.** If 2^k > p and x < 2^k − p, both x and x + p are integers below 2^k whose digit vectors satisfy every
constraint mod p.

**T1 (sketch).** Completeness: honest columns satisfy every row constraint, so Σ_x eq(τ, x)·Σ α^i C_i(x) = 0 and
the logUp grand sum is 0. Soundness: if some x_j ≥ 2^k, by L1/L2 no assignment satisfies all row constraints
*and* all lookups. Either a row constraint fails — then, except with probability (m_c − 1 + v)/p over (α, τ),
the zero-check claim 0 is false and the sum-check rejects except with probability v·d/p ([Thaler §4.1, The Sum-Check Protocol]);
or a lookup value is outside the table — then by L4 the logUp identity fails except with probability
(2(M + T) − 1)/p over β (poles included), so the grand sum (or the helper constraints) is wrong. Each round's
error is bounded as above, i.e. the protocol has round-by-round soundness with ε_rbr = max over rounds; the
non-interactive version follows by [CY24 §RBR soundness implies SR soundness, theorem:rbr-soundness-to-sr-soundness]
**provided every challenge is derived from the statement, the index and all previous prover messages**
(basic FS, [CY24 §Construction, construction:basic-fs-for-public-coin-ip]) — the precondition that the falsifier's
FS audit checks (C5).

## Assumption ledger — Theorem T1

| # | item | our choice | alternatives rejected (why) | source |
|---|---|---|---|---|
| A1 | relation R | R = {(x_1..x_n; acc, limb cells) : every x_j < 2^k}, index = circuit (selectors, table) for (arm, n, k, c) | — | circuits/*/SPEC.md |
| A2 | soundness notion | soundness (non-adaptive statement choice is **not** assumed: the statement is in the first hash) | knowledge soundness (needs a PCS extractor; the toy verifier reads columns) | [CY24 §Lack of adaptive security, section:fs-lack-of-adaptive-soundness] |
| A3 | ZK notion | none (the toy is not hiding) | — | — |
| A4 | model | ROM; SHA-256 transcript and Merkle hashing | — | [Thaler §5.1, The Random Oracle Model] |
| A5 | computational assumptions | none | — | — |
| A6 | setup | transparent | — | — |
| A7 | conjectures | none | — | — |
| A8 | input property of the interactive protocol | RBR soundness, ε_rbr = max(logUp, batching + zero-check, d/p) | ordinary soundness only (FS loss would be C(t+k, k)·ε) | [CY24 §RBR soundness implies SR soundness, theorem:rbr-soundness-to-sr-soundness] |
| A9 | security-level definition | both reported: worst-case and average-case | — | [CY24 §Security levels, section:security-levels] |

## Parameters and security

Generated by `theory/budget.py` (configs and full `soundness_calc.py` outputs: `results/soundness/<arm>_k<k>_<level>.{json,txt}`;
summary: `results/soundness/summary.md`). n = 64, c = 8, Goldilocks, λ = 256. All terms proven; no conjectured
terms. **The toy is insecure: 26–30 bits worst-case.**

### Soundness budget: toy argument, lookup arm, k = 64
Definition: worst-case. Notion: soundness. λ = 256, field Goldilocks, challenges in F_p, 22 rounds, 5 Merkle trees of 2^10 leaves.

| term | bound ε_i(t) | bits at t = 2^26 | proven / conjectured / heuristic | source | EVIDENCE |
|---|---|---|---|---|---|
| IOP via RBR | (t + 22)·1535/p | 27.42 | proven | CY24 RBR theorem; Thaler §3.4, §4.1; logUp (ePrint 2022/1530) | E20 |
| Merkle multi-extraction | CY24 lemma, 5 trees × 2^10 leaves | 202.68 | proven | CY24 mt-multi-configuration-multi-extractability | E20 |
| **total (union bound)** | Σ | **26 bits** | proven | | E20 |

Average-case (same terms): **48 bits** (E21).

### Soundness budget: toy argument, bits arm, k = 64
Definition: worst-case. λ = 256, Goldilocks, 14 rounds, 1 Merkle tree of 2^13 leaves.

| term | bound ε_i(t) | bits at t = 2^30 | proven / conjectured / heuristic | source | EVIDENCE |
|---|---|---|---|---|---|
| IOP via RBR | (t + 14)·15/p | 30.09 | proven | CY24 RBR theorem; Thaler §3.4, §4.1 | E22 |
| Merkle multi-extraction | CY24 lemma, 1 tree × 2^13 leaves | 194.68 | proven | CY24 lemma | E22 |
| **total (union bound)** | Σ | **30 bits** | proven | | E22 |

Average-case: **56 bits** (E23). All grid points: bits arm 30 (worst) / 56–57 (average); lookup arm 26–27 /
48–50 (`results/soundness/summary.md`).

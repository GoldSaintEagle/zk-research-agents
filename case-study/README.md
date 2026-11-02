# case-study/ — end-to-end example (TEACHING EXAMPLE)

A toy ZK research project run through all phases P0–P8 with the 13 agents, using only public, textbook-level
material, insecure toy parameters and a pure-Python toy prover. **Do not cite any number from here.**

| path | what |
|---|---|
| [`WALKTHROUGH.md`](WALKTHROUGH.md) | phase-by-phase narration: command → agent → files read/written → gate → loops; reproduction commands; lessons |
| [`../docs/zh/case-study-walkthrough.md`](../docs/zh/case-study-walkthrough.md) | Chinese version |
| [`toy-rangecheck/`](toy-rangecheck/) | the project: blackboard files (`STATE.md`, `CLAIMS.md`, `EVIDENCE.md`, …) at its top level ([its README](toy-rangecheck/README.md) maps every directory to its agent) |
| `toy-rangecheck/circuits/` | R1CS and Plonkish bit decomposition, Plonkish + logUp limbs, with SPECs, counts and the builder self-audit |
| `toy-rangecheck/impl/` | toy multilinear Plonkish prover/verifier (zero-check + logUp over Goldilocks, Fiat–Shamir, Merkle) on `cryptomath.zk` |
| `toy-rangecheck/falsify/` | one script + log per attack (exhaustive circuit audit, FS forgery, budget recomputation, edge runs) and the tally |
| `toy-rangecheck/results/` | crbench logs (`run.json`, per-execution `r*.log`, `summary.log`), soundness budgets, sanitised |
| `toy-rangecheck/paper/` | 7-page LNCS write-up (`main.pdf`), audit-tex / anon-check / pdf-check logs |

Topic: k-bit range checks for n = 64 values over Goldilocks, written (a) as R1CS / Plonkish bit decomposition and
(b) as Plonkish + logUp lookups with 8-bit limbs, compared in rows and in toy prover time on one backend.

Outcome: the P0 thesis "lookups are ≥ 5× cheaper for every k ≤ 64" did not survive. Padded rows: 8× fewer for
16 ≤ k ≤ 63, but only 2× at k = 4 (the 2^8-row table sets the height). Prover time: 3.7×–3.8× faster for
16 ≤ k ≤ 48, no faster at k = 4 (0.96×; 1.00× in a re-run), 25× slower with 16-bit limbs. k = 64 is not a range check in Goldilocks.
The falsifier also caught the planted under-constrained top limb (exhaustive audit over F_11) and a Fiat–Shamir
transcript that let the toy prover prove a false statement.

Quick start (≈ 2 min, one core; details in the walkthrough):

```bash
cd case-study/toy-rangecheck
python3 circuits/selfcheck.py && python3 falsify/C1_lookup_circuit/audit.py && python3 falsify/C5_fs/attack.py
python3 code/run_experiments.py --only bench_kscan --out results-rerun   # re-measure into an ignored directory
```

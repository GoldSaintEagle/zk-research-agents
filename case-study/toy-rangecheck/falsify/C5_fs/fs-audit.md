# FS audit — toy argument, paper THEORY.md T1, code impl/toy_prover.py v1 → v2; auditor: falsifier
FS variant cited: basic ([CY24 §Construction, construction:basic-fs-for-public-coin-ip]) · interactive input notion: RBR (THEORY.md A8)

| # | check | paper | code v1 | code v2 | evidence |
|---|---|---|---|---|---|
| 1 | statement in first hash — **of every transcript** | PASS | **FAIL** | PASS | v1: the zero-check and grand-sum sum-checks call `sumcheck.prove_fs` without a transcript, i.e. a fresh `Transcript(label)` absorbing only (p, v, d, claim) and the messages; attack.log: r_0..r_v unchanged when only the statement changes; 4/4 forged proofs of x_0 = 2^k accepted |
| 2 | messages before challenges, in order | PASS | FAIL (commitments not in the sum-check transcript) | PASS | same |
| 3 | SR / RBR proven | PASS | n.a. | n.a. | THEORY.md T1, A8 |
| 4 | hash-chain conditions | n.a. | n.a. | n.a. | basic FS |
| 5 | salts for ZK | n.a. | n.a. | n.a. | no ZK claimed |
| 6 | domain separation | PASS | PASS | PASS | labels distinct; v2 absorbs `sumcheck:<label>` before each sub-protocol |
| 7 | uniform challenges | PASS | PASS | PASS | 128 extra bits; bias term in falsify/C6_soundness |
| 8 | parameters hashed | PASS | PASS (outer only) | PASS | |
| 9 | verifier recomputes challenges | PASS | PASS | PASS | |
| 10 | grinding nonce | n.a. | n.a. | n.a. | |

Why the builder's self-audit passed v1: it ran the skill's sensitivity test on the **first** challenge only, and its
transcript recorder looked only at the outer transcript object. Re-proving honestly does not reveal the gap either
(honest messages change with the statement); the test that does is *fixed prover messages, different statement*.

Verdict: v1 FAIL (C5 refuted); v2 PASS (C10 survived). Fix: `lib/cryptomath` `sumcheck.prove_fs/verify_fs(...,
transcript=)` and the prover continues its outer transcript (DECISIONS D-6).

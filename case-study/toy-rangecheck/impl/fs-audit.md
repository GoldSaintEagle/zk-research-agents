# FS audit — toy argument (impl/toy_prover.py v1), auditor: builder (prover-engineer), 2026-11-02
FS variant cited: basic FS ([CY24 §Construction, construction:basic-fs-for-public-coin-ip]) · interactive input notion: RBR (THEORY.md T1, A8)

| # | check | paper | code | evidence |
|---|---|---|---|---|
| 1 | statement in first hash | PASS | PASS | `statement_transcript` absorbs arm, n, k, c, p, H, index digest, every x_j; sensitivity test of the first challenge (results/selfcheck/fs_builder_v1.log) |
| 2 | messages before challenges, in order | PASS | PASS | transcript lint vs THEORY order (roots, beta, helper roots, tau, alpha) |
| 3 | SR / RBR proven | PASS | n.a. | THEORY.md T1 sketch, A8 |
| 4 | hash-chain conditions | n.a. | n.a. | basic FS (running SHA-256 state), not a hash chain |
| 5 | salts for ZK | n.a. | n.a. | no ZK claimed (A3) |
| 6 | domain separation | PASS | PASS | tags distinct and prefix-free (self-audit log) |
| 7 | uniform challenges | PASS | PASS | `challenge_scalar` with 128 extra bits |
| 8 | parameters hashed | PASS | PASS | n, k, c, p, H and the index digest absorbed |
| 9 | verifier recomputes challenges | PASS | PASS | the proof has no challenge field; tampered message rejected |
| 10 | grinding nonce | n.a. | n.a. | no proof of work |

Verdict (builder): PASS. Handed to falsifier for the independent re-run (P6).

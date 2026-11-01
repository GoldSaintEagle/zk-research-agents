---
description: Run a fair interleaved ZK benchmark and record evidence
argument-hint: <spec>
---

Use the experimenter agent with skills bench-protocol and log-to-evidence: $ARGUMENTS. Baselines come from baselines/MANIFEST.md at a pinned SHA (skill baseline-pin; catalogue and crbench parser per library in references/baselines/MANIFEST.md, recipes in `crbench adapters`). Same statement, same soundness bits / regime / level definition, same timing scope (witness generation, preprocessing, proving, recursion, verification each separate), same threads and hardware features. Run interleaved repeats with crbench (lib/bench), verify every timed proof, and report prover time, verifier time, proof size and peak memory (median + IQR); constraint / row counts come from compiler output via skill constraint-cost. Compare with the prediction of skill prover-cost-model phase by phase. Capture the environment, add EVIDENCE.md rows, produce Markdown + LaTeX tables.

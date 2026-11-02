# bench_kscan — protocol (fixed 2026-11-02 before the first run; owner: experimenter, skills/bench-protocol)

- **Claims tested:** C4 (prover time ratio ≥ 5× for every k ≤ 64); C3/C7 use the deterministic counts
  (`results/counts/`).
- **What would refute C4:** any grid point whose bits/lookup median ratio, or the upper end of its 95 % paired
  bootstrap CI, is below 5.
- **Arms:** `impl/prove.py --arm bits|lookup --k K --n 64 --c 8`, K ∈ {4, 8, 12, 16, 24, 32, 48, 64}; same prover,
  transcript, field and hash for both arms (baselines/MANIFEST.md); soundness level of each arm: THEORY.md
  (worst-case definition; the lookup arm is 3–4 bits lower, D-4).
- **Metric:** process CPU time of circuit build + prove (`prove time:` line, crbench generic parser, label
  `prove`); wall time logged next to it (`prove_wall elapsed`). Per-phase lines for the cost-model comparison.
- **Verification inside the timed binary:** every execution verifies its proof after the timer stops and exits
  1 if it does not verify (crbench keeps it as a failure).
- **Session:** all 16 arms interleaved in one session, alternating order, 1 warm-up + 7 rounds, threads = 1,
  crbench lock held, environment captured in `run.json`.
- **Absolute times are meaningless** (pure Python toy); only ratios between arms on this backend are reported.

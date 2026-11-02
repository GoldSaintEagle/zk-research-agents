# impl/BUILD.md (owner: prover-engineer)

- Interpreter: the project venv's CPython 3 (version captured in every `run.json` "env"); no C extensions in the
  timed code (the prover uses Python ints; numpy is used only by crbench's statistics, outside the timer).
- Threads: 1 (`OMP_NUM_THREADS=OPENBLAS_NUM_THREADS=1`, set by crbench `--threads 1`); one process per execution.
- Timer: `time.process_time()` around build + prove (CPU time of the process; the machine is a shared laptop, so
  wall time is logged next to it as `prove_wall elapsed` but not used, cf. the old case's lesson on wall time).
- Both arms: identical code path (`impl/prove.py --arm bits|lookup`), identical transcript and Merkle code.
- Differences between arms: none in the build; the arms differ only in the circuit they prove.

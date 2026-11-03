# crbench — benchmark harness for ZK proof research

Dependency-light (numpy only). Python >= 3.10. Parsers cover the ZK toolchain (snarkjs / rapidsnark,
circom, gnark, halo2 / arkworks / plonky3 via criterion, nargo, RISC Zero, SP1); adapters are recipes,
not vendored code (fetch, pin and build are in `references/baselines/MANIFEST.md`).

```bash
pip install -e lib/bench          # or: PYTHONPATH=lib/bench python3 -m crbench ...
crbench run -a base='./bench_old --toy' -a new='./bench_new --toy' \
            -n 7 -w 1 --parser generic --threads 1 --cpus 2 --log-dir results/toy-ab --target ./build
crbench table results/toy-ab/run.json --latex --evidence new:speedup=E3
crbench evidence add EVIDENCE.md --printed '2.02×' --command 'derived: E1/E2' --log -
crbench evidence check EVIDENCE.md --root .
crbench audit-tex paper/main.tex EVIDENCE.md      # exit 1 if any number is untraced
crbench stale build/bench src/                    # exit 1 if a source is newer than the binary
crbench parsers ; crbench adapters
```

| module | purpose |
|---|---|
| `stats` | median, IQR, bootstrap CI, speed-up of medians with (paired) bootstrap CI |
| `runner` | interleaved rounds (alternate / shuffle / fixed), warm-up, repeats, timeout, thread vars, `taskset` pinning, per-execution logs + `run.json`, failures kept in the ledger |
| `envcapture` | CPU / governor / load / compilers / git commit+dirty of target / perf env vars; warnings |
| `lock` | advisory `flock` so benches never overlap |
| `parsers` | registry (`crbench parsers`): generic, criterion (arkworks, halo2, plonky3), gobench, gbench, shell-time, snarkjs, rapidsnark, circom, gnark, nargo-info, risc0, sp1, sat, gnu-time; `register_parser`, `regex_parser` |
| `tables` | Markdown + LaTeX booktabs; cells carry EVIDENCE IDs (`\evid{E3}`) |
| `evidence` | EVIDENCE.md reader/writer/validator; `audit_tex` |
| `adapters` | per-library recipe (parser + typical command + fairness note): arkworks, gnark, gnark-log, circom, snarkjs, rapidsnark, halo2, plonky3, nargo, risc0, sp1, sat, gnu-time |

## audit-tex rules

A number is *measurement-like* if it has a decimal point, a thousands separator, a
unit right after it (`s ms µs MB kB KiB bits × % cycles rounds constraints rows gas` ...,
the units of `skills/phase-gate/scripts/gate_check.py`), or is an exponent
(`2^{128}`). Each such number in the document body must appear in the printed column
of some EVIDENCE.md row (numeric match after normalisation: `1{,}536` = `1,536` =
`1536`; `2.50` = `2.5`). `\evid{ID}` tags additionally check the preceding number
against that specific row. Escape hatches: `% crbench:ignore` on a line, or a
`% crbench:ignore-begin` / `% crbench:ignore-end` block — each use should be
justified in the ledger or DECISIONS.md. `--strict` audits bare integers too.

## ZK log parsers: format sources

All parser tests use synthetic logs. Where the format comes from:

| parser | source of the format | status |
|---|---|---|
| `snarkjs` | snarkjs README (`snarkjs r1cs info` example output) | counts verified; the exact verify line `snarkJS: OK!` needs verification |
| `rapidsnark` | none printed by the tool by default: time it with the shell | needs verification for builds with optional logging |
| `circom` | compile summary seen in public build logs and tutorials | needs verification (no sample in the official docs) |
| `gnark` | `logger/logger.go` (zerolog console writer) and `backend/groth16/*/prove.go` (`prover done`, `took` in ms) | compile-time `nbConstraints` line needs verification |
| `criterion` (halo2, plonky3, arkworks) | criterion command-line output | existing parser, tested on halo2-style names |
| `nargo-info` | noir `tooling/noirc_artifacts_info` (table header, `--json` fields) | older column layouts need verification |
| `risc0` | risc0 `host/prove_info.rs`, `Display for SessionStats` (logged with `RISC0_INFO=1`) | older `total cycles` / `user cycles` lines need verification |
| `sp1` | sp1 `examples/fibonacci/script/src/main.rs` (`executed program with N cycles`) | `Number of cycles:` variant needs verification |

Tests: `python3 -m pytest -q lib/bench/tests` (or `python3 -m unittest discover -s lib/bench/tests`).

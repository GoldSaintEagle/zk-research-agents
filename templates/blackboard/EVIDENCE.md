# EVIDENCE — every number in the paper traces to a log

> Owner: `experimenter`. Audited by `falsifier` and by `crbench audit-tex paper/main.tex EVIDENCE.md`.
> Columns are the SPEC §3 ledger format that `crbench evidence add/check`, `gate_check.py` and
> `soundness_calc.py --evidence` read and write; say what a number means in the command or in the paper, not in
> an extra column.

| ID | number/fact as printed in paper | command | log path | commit | machine | date | runs/median |
|---|---|---|---|---|---|---|---|
| E1 | 1.9× | `crbench run -a base=... -a new=... --log-dir results/S` (speedup of X over B at set S) | results/S/run.json | abc1234 | host:ab12cd / 1 thr | YYYY-MM-DD | 5 interleaved / median |

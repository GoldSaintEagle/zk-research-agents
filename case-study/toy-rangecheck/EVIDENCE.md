# EVIDENCE — every number in the paper traces to a log

> Owner: `experimenter`. Rebuilt by `code/ledger.py` from raw logs; audited by `falsifier` and by
> `crbench audit-tex`. Machine: one laptop core (hashed host in each row); date = date of the run.
> Times are pure-Python toy CPU times: only ratios between arms are printed in the paper.

| ID | number/fact as printed in paper | command | log path | commit | machine | date | runs/median |
|---|---|---|---|---|---|---|---|
| E1 | Table 1 (counts, circuits v2, n = 64, c = 8, k in {4..64}) | python3 circuits/count.py | results/counts/counts.log | code:c1fa191d53 | host:29e583a2ecd7 / 1 thr | 2026-11-03 | 1 / exact |
| E2 | 4160 constraints | python3 circuits/count.py  (R1CS bits, k = 64) | results/counts/counts.log | code:c1fa191d53 | host:29e583a2ecd7 / 1 thr | 2026-11-03 | 1 / exact |
| E3 | 8192 rows | python3 circuits/count.py  (bits arm, padded height, k = 64) | results/counts/counts.log | code:c1fa191d53 | host:29e583a2ecd7 / 1 thr | 2026-11-03 | 1 / exact |
| E4 | 1024 rows | python3 circuits/count.py  (lookup arm, padded height, k = 64) | results/counts/counts.log | code:c1fa191d53 | host:29e583a2ecd7 / 1 thr | 2026-11-03 | 1 / exact |
| E5 | 2× | python3 circuits/count.py  (padded-height ratio bits/lookup, k = 4) | results/counts/counts.log | code:c1fa191d53 | host:29e583a2ecd7 / 1 thr | 2026-11-03 | 1 / exact |
| E6 | 4× | python3 circuits/count.py  (padded-height ratio bits/lookup, k = 8) | results/counts/counts.log | code:c1fa191d53 | host:29e583a2ecd7 / 1 thr | 2026-11-03 | 1 / exact |
| E7 | 8× | python3 circuits/count.py  (padded-height ratio bits/lookup, k = 16) | results/counts/counts.log | code:c1fa191d53 | host:29e583a2ecd7 / 1 thr | 2026-11-03 | 1 / exact |
| E8 | 256 rows | python3 circuits/count.py  (logUp table [0, 2^8)) | results/counts/counts.log | code:c1fa191d53 | host:29e583a2ecd7 / 1 thr | 2026-11-03 | 1 / exact |
| E10 | 0.96× | python3 code/run_experiments.py --only bench_kscan  (median CPU-time ratio bits/lookup, k = 4; paired bootstrap 95% CI [0.95, 0.96]) | results/bench_kscan/run.json | code:c1fa191d53 | host:29e583a2ecd7 / 1 thr | 2026-11-02 | 7 interleaved / median |
| E11 | 2.14× | python3 code/run_experiments.py --only bench_kscan  (median CPU-time ratio bits/lookup, k = 8; paired bootstrap 95% CI [2.12, 2.16]) | results/bench_kscan/run.json | code:c1fa191d53 | host:29e583a2ecd7 / 1 thr | 2026-11-02 | 7 interleaved / median |
| E12 | 1.66× | python3 code/run_experiments.py --only bench_kscan  (median CPU-time ratio bits/lookup, k = 12; paired bootstrap 95% CI [1.65, 1.68]) | results/bench_kscan/run.json | code:c1fa191d53 | host:29e583a2ecd7 / 1 thr | 2026-11-02 | 7 interleaved / median |
| E13 | 3.69× | python3 code/run_experiments.py --only bench_kscan  (median CPU-time ratio bits/lookup, k = 16; paired bootstrap 95% CI [3.62, 3.71]) | results/bench_kscan/run.json | code:c1fa191d53 | host:29e583a2ecd7 / 1 thr | 2026-11-02 | 7 interleaved / median |
| E14 | 3.74× | python3 code/run_experiments.py --only bench_kscan  (median CPU-time ratio bits/lookup, k = 24; paired bootstrap 95% CI [3.68, 3.79]) | results/bench_kscan/run.json | code:c1fa191d53 | host:29e583a2ecd7 / 1 thr | 2026-11-02 | 7 interleaved / median |
| E15 | 3.81× | python3 code/run_experiments.py --only bench_kscan  (median CPU-time ratio bits/lookup, k = 32; paired bootstrap 95% CI [3.78, 3.83]) | results/bench_kscan/run.json | code:c1fa191d53 | host:29e583a2ecd7 / 1 thr | 2026-11-02 | 7 interleaved / median |
| E16 | 3.73× | python3 code/run_experiments.py --only bench_kscan  (median CPU-time ratio bits/lookup, k = 48; paired bootstrap 95% CI [3.71, 3.78]) | results/bench_kscan/run.json | code:c1fa191d53 | host:29e583a2ecd7 / 1 thr | 2026-11-02 | 7 interleaved / median |
| E17 | 3.98× | python3 code/run_experiments.py --only bench_kscan  (median CPU-time ratio bits/lookup, k = 64; paired bootstrap 95% CI [3.95, 4.03]) | results/bench_kscan/run.json | code:c1fa191d53 | host:29e583a2ecd7 / 1 thr | 2026-11-02 | 7 interleaved / median |
| E40 | 2.07× | python3 falsify/C4_time/edges.py  (median CPU-time ratio bits/lookup, c = 4, n = 64, k = 32; paired bootstrap 95% CI [2.06, 2.09]) | results/falsify_C4_edges/run.json | code:c1fa191d53 | host:29e583a2ecd7 / 1 thr | 2026-11-02 | 5 interleaved / median |
| E41 | 3.77× | python3 falsify/C4_time/edges.py  (median CPU-time ratio bits/lookup, c = 8, n = 64, k = 32; paired bootstrap 95% CI [3.73, 3.79]) | results/falsify_C4_edges/run.json | code:c1fa191d53 | host:29e583a2ecd7 / 1 thr | 2026-11-02 | 5 interleaved / median |
| E42 | 0.04× | python3 falsify/C4_time/edges.py  (median CPU-time ratio bits/lookup, c = 16, n = 64, k = 32; paired bootstrap 95% CI [0.04, 0.04]) | results/falsify_C4_edges/run.json | code:c1fa191d53 | host:29e583a2ecd7 / 1 thr | 2026-11-02 | 5 interleaved / median |
| E43 | 1.05× | python3 falsify/C4_time/edges.py  (median CPU-time ratio bits/lookup, c = 8, n = 16, k = 16; paired bootstrap 95% CI [1.03, 1.07]) | results/falsify_C4_edges/run.json | code:c1fa191d53 | host:29e583a2ecd7 / 1 thr | 2026-11-02 | 5 interleaved / median |
| E20 | 26 bits | python3 theory/budget.py  (lookup arm, k = 64, worst-case, proven) | results/soundness/lookup_k64_worst-case.txt | code:c1fa191d53 | n/a (exact computation) | 2026-11-03 | 1 / exact |
| E21 | 48 bits | python3 theory/budget.py  (lookup arm, k = 64, average-case, proven) | results/soundness/lookup_k64_average-case.txt | code:c1fa191d53 | n/a (exact computation) | 2026-11-03 | 1 / exact |
| E22 | 30 bits | python3 theory/budget.py  (bits arm, k = 64, worst-case, proven) | results/soundness/bits_k64_worst-case.txt | code:c1fa191d53 | n/a (exact computation) | 2026-11-03 | 1 / exact |
| E23 | 56 bits | python3 theory/budget.py  (bits arm, k = 64, average-case, proven) | results/soundness/bits_k64_average-case.txt | code:c1fa191d53 | n/a (exact computation) | 2026-11-03 | 1 / exact |
| E30 | accepts 8 (k = 3, c = 2, F_11) | python3 falsify/C1_lookup_circuit/audit.py  (exhaustive, circuits v1) | falsify/C1_lookup_circuit/audit.log | code:c1fa191d53 | n/a (exact computation) | 2026-11-03 | 1 / exact |
| E31 | 2^12 | python3 falsify/C1_lookup_circuit/audit.py  (Goldilocks witness, circuits v1, k = 12) | falsify/C1_lookup_circuit/audit.log | code:c1fa191d53 | n/a (exact computation) | 2026-11-03 | 1 / exact |
| E32 | 4/4 forged proofs accepted | python3 falsify/C5_fs/attack.py  (prover v1) | falsify/C5_fs/attack.log | code:c1fa191d53 | n/a (exact computation) | 2026-11-03 | 1 / exact |

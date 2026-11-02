# 案例走读：toy-rangecheck（逐阶段）——教学示例

> **这是什么。** 一个完整、可运行的玩具 ZK 研究项目，用来演示本工具包的 13 个 agent 如何通过黑板文件交接工作，
> 以及每个阶段门禁检查什么。题目公开且属于教科书层面：在 Goldilocks 域上对 n = 64 个值做 k 位范围检查，比较
> (a) 按位分解（R1CS，以及 Plonkish 的 running-sum 门）与 (b) Plonkish + logUp 查表（8 位 limb）
> （[Thaler §6.5.4, Details of the Transformation]；[Thaler §6.6.3, Efficiently Representing Non-Arithmetic Operations Over Large Prime-Order Fields]；logUp 见 ePrint 2022/1530）。
> 参数不安全（26–30 位）；计时是纯 Python 玩具 prover 的 CPU 时间，**只有同一后端上两种写法之间的比值有意义**。
> 这里没有任何研究结论。
>
> **如何产生。** 由一个 Claude Code 会话依次扮演各个角色，每次都按照 `agents/<id>.md` 及其列出的 skill 执行；
> 所有数字都由下列脚本于 2026-11-02 实测得到。安装插件后，可用每个阶段列出的斜杠命令驱动同样的流程（或用
> `/cra-phase P<k>`）。P6 按 `skills/falsify` 手动执行（多 agent 的 `workflows/falsify-round.js` 需要用户明确同意
> 多 agent 编排），但 falsifier 各视角的投票仍用该 workflow 经过测试的 `tally()` 汇总（`falsify/tally.mjs`）。
> 这次运行同时是整个工具包的端到端验收，发现的问题列在文末。

项目目录：`case-study/toy-rangecheck/`（黑板文件在其顶层，其 README 列出每个目录归哪个 agent 管）。
英文原版：`case-study/WALKTHROUGH.md`。

## 如何复现

需要 Python ≥ 3.10（含 numpy、sympy、matplotlib；例如 `python3 -m venv .venv && .venv/bin/pip install numpy sympy
matplotlib pymupdf`，之后用 `.venv/bin/python` 代替 `python3`）、Node ≥ 18、带 latexmk 的 TeX。单核：
`export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1`。代码会自行把 `lib/cryptomath` 和 `lib/bench` 加入 `sys.path`。

**A. 所有确定性的结果（约 1 分钟）。** 用代码和已提交的原始测量日志重新生成每一个日志、表格、台账行、图和
PDF；跑完后 `git status` 除日期、commit 哈希、PDF 字节以及成本模型用微基准测得的单位成本
（`results/bench_kscan/cost-model.md`、`prediction.json`）外应无变化。

```bash
cd case-study/toy-rangecheck
python3 circuits/range_gadgets.py && python3 impl/toy_prover.py                 # 自检（< 1 秒）
python3 ../../skills/constraint-cost/scripts/constraint_count.py --n 64 --k 12 --c 4 8 16   # P2 规划计数器
python3 theory/check_gadgets.py > theory/check_gadgets.log                      # P3 引理，穷举
python3 theory/budget.py > results/soundness/summary.md                         # P3 soundness 预算
python3 circuits/selfcheck.py > results/selfcheck/circuits_v2.log               # P5 建造者电路自查
python3 impl/fs_selfaudit.py > results/selfcheck/fs_builder_v2.log              # P5 建造者 FS 自查
python3 code/run_experiments.py --only counts                                   # P5 约束/行数（确定性）
python3 code/cost_model.py --predict && python3 code/cost_model.py --compare    # P5 预测与实测对比
python3 falsify/C1_lookup_circuit/audit.py > falsify/C1_lookup_circuit/audit.log   # P6 穷举电路审计（约 5 秒）
python3 falsify/C5_fs/attack.py > falsify/C5_fs/attack.log                      # P6 FS 敏感性 + 伪造
python3 falsify/C3_C7_counts/recount.py > falsify/C3_C7_counts/recount.log
python3 falsify/C4_time/recompute.py > falsify/C4_time/recompute.log            # 从原始 run.json 重算比值
python3 falsify/C6_soundness/recompute.py > falsify/C6_soundness/recompute.log  # 独立重算预算
node falsify/tally.mjs > falsify/tally.log                                      # 用 falsify-round 的 tally() 定判
python3 code/run_experiments.py --sanitise-only                                 # 清除家目录、用户名、主机名、代理
python3 code/ledger.py                                                          # 由原始日志重建 EVIDENCE.md 并检查
python3 code/make_figures.py                                                    # P7 图，只读 run.json 与 counts.log
(cd paper && make)                                                              # P7 PDF（llncs 取自 TeX 发行版）
for f in paper/main.tex paper/sections/*.tex; do
  PYTHONPATH=../../lib/bench python3 -m crbench audit-tex "$f" EVIDENCE.md --check-ledger --root .
done                                                                            # 每个数字都有台账行
python3 ../../skills/camera-ready/scripts/pdf_checks.py paper/main.pdf --log paper/main.log --limit 8
for ph in P0 P1 P2 P3 P4 P5 P6 P7 P8; do
  python3 ../../skills/phase-gate/scripts/gate_check.py --project . --phase $ph --paper paper
done                                                                            # 九个阶段全部 PASS
```

匿名性检查需要一份放在仓库之外的私有 deny-list：
`python3 ../../skills/anonymize-check/scripts/anon_check.py paper/sections paper/main.tex paper/macros.tex refs.bib paper/main.pdf paper/figs --deny-file <你的名单> --allow-url-file paper/.allow_urls.txt`。

**B. 重新测量（约 1.5 分钟；数值会有几个百分点的波动）。** 写入被 git 忽略的 `results-rerun/`，因此已提交的证据
与论文保持一致；把比值与 `results/*/summary.log` 对比即可。

```bash
python3 code/run_experiments.py --only bench_kscan --out results-rerun          # P5：16 个 arm × (1 + 7) 次
python3 falsify/C4_time/edges.py --out results-rerun                            # P6 边界运行：c = 4/8/16，n = 16
diff <(cut -d' ' -f1,6-8 results/bench_kscan/summary.log) <(cut -d' ' -f1,6-8 results-rerun/bench_kscan/summary.log)
```

**C. 需要联网**（Crossref / ePrint；镜像回退见 `skills/bib-verify`）：

```bash
python3 ../../skills/bib-verify/scripts/verify_bib.py refs.bib > bib-verify-report.md     # P1/P8：18/18 VERIFIED
python3 ../../skills/eprint-search/scripts/eprint_search.py "lookup range check" --months 12  # P1 新颖性检索记录
```

## 各阶段

### P0 立项 · `/cra-init case-study/toy-rangecheck`，然后 `/cra-phase P0`
- **Agent：** `pi-orchestrator`。**读：** 一句话题目、`workflows/PHASES.md`。
- **写：** 从 `templates/blackboard/` 初始化黑板（即 `/cra-init` 的动作）；`STATE.md` 写入故意过强的 thesis v0：
  *"在 Goldilocks 上对 n = 64 个值，8 位 limb 的 logUp 比按位分解至少便宜 5×——无论约束/行数还是 prover 时间——
  对所有 k ≤ 64 成立"*；论文类型（应用/电路 + 玩具系统 → 13 个 agent 全部参与）、模拟会议、kill 日期与 kill 条件；
  `DECISIONS.md` D-1：两种写法跑在**同一个**我们自己的后端上，只报告比值。
- **门禁 P0：** PASS（7 项）。

### P1 文献 · `/cra-lit "lookup range check"`
- **Agent：** `lit-scout`（skill：`lit-matrix`、`bib-verify`、`eprint-search`、`textbook-index`）。
- **读：** `references/reading-lists/` 中的 `lookup.md`、`piop-arithmetization.md`、`circuit-security.md`、
  `fiat-shamir-soundness.md`；两本参考书的导读图。
- **写：** `LITERATURE.md`（16 篇；真正的竞争者 plookup、logUp、cq、Lasso 加粗；每个竞争者的阅读笔记；
  `lit_matrix.py` 检查 OK）；`refs.bib` 与 `bib-verify-report.md`（**18/18 VERIFIED**，两本书在 P7 加入：Thaler 经
  DOI 核实，CY24 按 `references/books/README.md` 走 URL 路径，带访问日期和存档 URL）；`MATH-REFS.md`（M1–M10，
  按参考书引用格式书写，经 `scripts/check_book_refs.py` 检查）；新颖性检索记录。
- **门禁 P1：** PASS，一项豁免（`[~] … WAIVED: … (DECISIONS D-2)`：这一权衡属于教科书内容）。

### P2 构思 · `/cra-ideas "lookups vs bits for range checks"`
- **Agent：** `idea-miner`（skill `idea-mining-loop`，成本代理 `constraint-cost`）；`falsifier` 做筛选。
- **读：** 规划计数器 `skills/constraint-cost/scripts/constraint_count.py --n 64 --k K --c 4 8 16`。
- **写：** `IDEAS.md`——I1（8 位 limb + logUp）晋级；I2（16 位 limb）**在筛选时被否决**（2^16 行的表决定了高度）；
  I3（running-sum 门）被采纳为**基线**，因为普通三线按位写法会夸大收益。Gate A（被释放的参数：limb 宽度 c）与
  Gate B（反常：小 k 时表高度构成下限）。`CLAIMS.md` 登记 C1–C7，全部 `open`。规划数字已经预示 k ≤ 12 时达不到
  5×；但故意保持原表述——规划计数器不是我们的电路。
- **门禁 P2：** PASS（一项豁免，D-2）。

### P3 理论 · `/cra-phase P3`、`/cra-soundness`
- **Agent：** `theorist`（skill：`sage-check`、`zk-definitions`、`soundness-budget`）。
- **写：** `THEORY.md`：L1（2^k < p 时 running sum 恰好接受 [0, 2^k) 且见证唯一）、L2（limb + **顶部 limb 检查**）、
  L2n（没有顶部 limb 检查时接受集合是 [0, 2^(cL))）、L3（Goldilocks 中 k = 64 不是范围检查：5 与 5 + p 都能分解）、
  L4（logUp 计数上界）；`theory/check_gadgets.py`（每条命题一行 JSON，在 F_11 … F_257 上穷举）；T1（玩具论证经
  RBR → state restoration 的可靠性，[CY24 §RBR soundness implies SR soundness, theorem:rbr-soundness-to-sr-soundness]）；
  假设台账 A1–A9；`theory/budget.py` 为每个网格点和每种定义生成一份 `soundness_calc.py` 配置，结果在
  `results/soundness/`：**worst-case 26–30 位，average-case 48–57 位**（[CY24 §Security levels, section:security-levels]）。
- **门禁 P3：** PASS。（theorist 自己的表已经与 C6 的"average-case ≥ 50 位"矛盾；该主张留给 falsifier 裁决。）

### P4 基线 · `/cra-phase P4`
- **Agent：** `baseline-engineer`（skill `baseline-pin`），`prover-engineer` 配合（`impl/BUILD.md`）。
- **写：** `baselines/MANIFEST.md`：bits arm 使用相同的 prover、transcript、域、哈希、解释器和计时范围；在任何数字
  出现之前就把 R1CS 标为与 Plonkish 行数*不可同口径比较*；生产库不在范围内。D-4：同一安全级别签认（同一脚本、
  同一定义；lookup arm 多出的 logUp 项使其低 3–4 位）。
- **门禁 P4：** PASS（一项豁免：这个玩具后端没有已发表的数字，D-1/D-4）。

### P5 构建与测量 · `/cra-bench "bits vs lookup, k-scan"`、`/cra-circuit-audit`、`/cra-fs-audit`
- **circuit-engineer：** **先**写 `circuits/range_bits/SPEC.md` 与 `circuits/range_lookup/SPEC.md`（lookup 的 SPEC
  列出了第 4 条约束：顶部 limb 检查），再写 `circuits/range_gadgets.py`——v1 **漏掉了第 4 条约束**（故意埋的
  bug）。自查 `circuits/selfcheck.py`：每个 k 用 203 个随机值做差分测试、边界值、超范围输入（被见证生成器拒绝）、
  每类门变异一个单元格——**建造者 PASS**。`CIRCUITS.md` 各行的计数来自构建出的对象（`circuits/count.py`）。
- **prover-engineer：** `impl/toy_prover.py`（Merkle 承诺各列、对所有行约束做 zero-check、logUp 辅助列与总和、
  一条 FS transcript）——v1 调用库函数 `sumcheck.prove_fs`，它会**新开一条 transcript**。FS 自查
  `impl/fs_selfaudit.py`：按 THEORY 的顺序做 transcript lint、检查**第一个**挑战的敏感性、篡改测试、域分离标签——
  **建造者 PASS**（`impl/fs-audit.md`）。成本模型 `code/cost_model.py`：按阶段统计 Merkle 哈希与 sum-check 表求值次数，
  单位成本用微基准测得；占主导的阶段（zero-check、commit）处处在 1.5× 以内，较小的 logUp 阶段系统性地低估
  1.5–1.8×，已给出解释（`results/bench_kscan/cost-model.md`）。
- **experimenter：** 运行前先在 `results/bench_kscan/README.md` 固定测量方案；`code/run_experiments.py` 把 16 个
  arm 放在**同一次交替运行的 crbench 会话**中（1 次预热 + 7 轮，进程 CPU 时间，每个证明都验证）；`code/ledger.py`
  从原始 `run.json`、`counts.log` 和 soundness 输出重建 `EVIDENCE.md`（`crbench evidence check`：0 错误）。
- **门禁 P5：** 用 v1 电路 / v1 prover 时 PASS；P6 回环后用 v2 再次 PASS。

### P6 证伪门禁 · `/cra-falsify`（手动执行；投票用 `falsify-round.js` 的 `tally()` 汇总）
- **Agent：** `falsifier`（skill：`falsify`、`circuit-audit`、`fiat-shamir-audit`、`soundness-budget`）。每次攻击
  都是 `falsify/<claim>/` 下的脚本加日志；各视角的投票在 `falsify/votes.json`。
- **埋下的 bug 是怎么被发现的。** falsifier 依据 SPEC 而不是建造者的报告来设计测试，在 F_11 与 F_13 上以
  k = 3、c = 2 重新运行**真实的电路构建代码**，枚举每个见证单元格的所有赋值（`falsify/C1_lookup_circuit/audit.py`）：
  v1 接受 **8、9、10**（且小的 x 有两个见证）。在 Goldilocks 上 k = 12 时，它用 limb (16, 0) 接受 x = 2^12。
  建造者的随机差分测试看不到这个问题——诚实见证本来就满足更弱的约束系统——而它的超范围测试只检查了*见证生成器*
  会拒绝。同一审计还显示了两种写法在 k = 64 时的回绕问题，并且在 `skills/constraint-cost` 的规划计数器上发现了
  一个真实的工具包 bug（见下文）。
- **FS 审计发现了什么（不是故意埋的）。** 换一个陈述诚实地重新证明时，所有挑战都会变化，看起来没有问题。固定
  prover 的消息、只改变陈述，就会发现 sum-check 的挑战 r_0..r_v 不变：它们来自新开的 transcript。
  `falsify/C5_fs/attack.py` 据此伪造 x_0 = 2^k 的证明（全零消息固定了 r*，再选择陈述使公开列在 r* 处为零）：
  v1 验证者**接受 4/4**，修复后 0/4（[CY24 §Lack of adaptive security, section:fs-lack-of-adaptive-soundness]）。
- **回到 P5：** D-5（电路 v2：8 ∤ k 时每个值多一次移位查表；建造者把穷举检查加入自查）、D-6（prover v2 通过库新增的
  `transcript=` 参数延续外层 transcript）；重新计数与重新测量，v1 的汇总保存在 `results/superseded/`，没有对应的
  EVIDENCE 行。
- **其他攻击：** 从原始 `run.json` 重算比值（C4）；重算计数（C3、C7）；对 limb 宽度和陈述规模做边界测量
  （`falsify/C4_time/edges.py`：c = 4 → 2.07×，c = 16 → 0.04×，n = 16 → 1.05×）；按代码的实际布局独立计算预算，
  另加挑战采样偏差项（C6，与 THEORY 在每个网格点都一致）。

| 主张 | 判定 | 依据 |
|---|---|---|
| C1 lookup 电路正确，k ≤ 64 | **refuted** | 对 v1 的穷举审计（埋下的 bug）+ k = 64 回绕 |
| C2 按位分解正确，k ≤ 63 | **survived** | F_11/F_13 穷举（Plonkish 与 R1CS），L1 |
| C3 填充后行数少 ≥ 5×，所有 k ≤ 64 | **weakened** | 16 ≤ k ≤ 63 时 8×，k = 8、12 时 4×，k = 4 时 2×（表高度下限） |
| C4 prover 时间快 ≥ 5×，所有 k ≤ 64 | **weakened** | 处处低于 5×：16 ≤ k ≤ 48 时 3.7×–3.8×，k = 4 时不更快（0.96×；复现运行中为 1.00×）；写明了代价 |
| C5 transcript 通过 FS 审计 | **refuted** | 子 transcript 未绑定；伪造 4/4 |
| C6 worst-case ≥ 25 位 / average-case ≥ 50 位 | **weakened** | 重算：worst-case ≥ 26，average-case ≥ 48 |
| C7 约束数比 R1CS 少 ≥ 5× | **refuted** | 单位不一致（constraint-cost §1）；即使粗略比较，k = 4 时也只有 2.5× |
| C9 v2 lookup 电路正确，k ≤ 63 | **survived** | F_11/F_13/F_17 穷举，x = 2^12 被拒绝 |
| C10 v2 transcript 绑定每个挑战 | **survived** | 固定消息的敏感性测试，伪造 0/4 |

- **门禁 P6：** PASS。D-7 采纳 thesis v1（见 STATE.md）。

### P7 写作 + 作图 · `/cra-write <section>`、`/cra-figure "advantage vs k"`
- **Agent：** `writer`（skill `paper-playbook`）、`figure-artist`（skill `paper-figures`，`figures/PATTERNS.md` 的
  P12 模式，`figures/style/palette.py`）。
- **写：** 从 `templates/paper/` 复制出 `paper/`（LNCS、匿名版）；数字后带 `\evid{E…}` 标签；`code/make_figures.py`
  只从 `run.json` 与 `counts.log` 作图；`main.pdf` 共 7 页。
- **检查：** 对全部九个 .tex 文件运行 `crbench audit-tex`：0 错误（`paper/audit-tex.log`）；`gate_check.py --paper`
  PASS。定义性的数字（5× 目标、置信水平、实验方案参数、作为表大小的 2^16）带 `% no-evidence: <原因>`，两个检查器
  现在都接受这个标记。
- **门禁 P7：** PASS（P8 回环后再次 PASS）。

### P8 审稿 → 投稿（模拟）· `/cra-review "LNCS workshop"`、`/cra-submit`
- **Agent：** `reviewer-sim`（skill：`venue-calibration`、`mock-review`）、`submission-rebuttal`（skill：
  `anonymize-check`、`camera-ready`）。
- **写：** `reviews/REVIEW-BRIEF.md`；`REVIEWS.md` 第 R1 轮，审稿角色包括应用审稿人（这类论文必选）、soundness
  审稿人、实现与基准审稿人，以及可选的数据审计员和格式审计员（得分 4 / 4 / 3）。数据审计员发现了一个真实的不一致：
  摘要写的是"16 ≤ k ≤ 63 时 3.69×–3.98×"，但 3.98× 是 k = 64 的点——C4 的弱化表述也犯了同样的错。D-8 把它交给
  falsifier（重新给出表述）和 writer；实现审稿人指出的"没有 PCS"局限以及边界测量的数字（新增 EVIDENCE 行 E40–E43）
  也写进了论文。另有 `reviews/SUBMIT-FIXES.md`、`SUBMISSION.md`；`anon_check.py` HIGH=0 MEDIUM=0 LOW=5；
  `pdf_checks.py` RESULT OK。没有上传任何东西。
- **门禁 P8：** PASS（一项豁免：最终新颖性复查，因为不是真实投稿）。

## 这次运行发现的工具包问题（已在本批修复）

| 问题 | 发现阶段 | 修复 |
|---|---|---|
| `gate_check.py` 读不了自带模板：找不到 CLAIMS 的"EVIDENCE / THEORY refs"列和 EVIDENCE 的"value as printed"列，导致每个 survived 主张和每个论文数字都失败 | P5/P7 | 按表头关键词找列；selftest 直接在真实模板上运行 |
| `templates/blackboard/EVIDENCE.md` 有 9 列，而 `crbench evidence add` 与 `soundness_calc.py --evidence` 写的是 SPEC §3 的 8 列（写入的行错位） | P5 | 模板改用 SPEC 表头 |
| `gate_check.py` 按字面比较：`3.88\times` ≠ `3.88×`；`2^{2c}` 被当成数字 `2^{2` | P7 | 统一写法后再比较；忽略符号指数 |
| `crbench audit-tex` 把 `3.69$\times$--3.98$\times$` 里的范围短横当成负号 | P7 | 紧跟在另一个 `-` 后面的 `-` 不算符号 |
| 两个检查器的豁免标记不同（`% no-evidence:` 与 `% crbench:ignore`） | P7 | 互相接受对方的标记 |
| 论文模板用 `\ev{…}` 标注数字，而 crbench 只检查 `\evid{…}` | P7 | 模板改用 `\evid` |
| `lib/cryptomath` 的 `sumcheck.prove_fs/verify_fs` 只能新开 transcript，sum-check 子协议无法绑定到陈述 | P6 | 新增 `transcript=` 参数，并用伪造攻击写了测试 |
| `constraint_count.py::plonk_lookup`（规划计数器）没有约束 `acc_0`——接受任意 x——且最后一行的 limb 单元格不受约束 | P6 | 加 `zero` 门，去掉填充单元格，selftest |
| `toy_fs_attack.py::transcript_lint` 处理不了同一类条目在两轮中都被吸收的情况 | P5 | 改为子序列匹配，selftest |
| fiat-shamir-audit 流程中的敏感性测试（第一个挑战、诚实重证）看不出未绑定的子 transcript | P6 | 更新流程与陷阱列表 |
| `soundness_calc.py --evidence` 的日志路径只是占位符 | P3 | 新增 `--log PATH` |
| 匿名检查的 URL 白名单模板不含参考书自身的 URL | P8 | 已加入 |
| `scripts/privacy_scan.sh` 在 macOS 上生成空模式（BSD `paste` 需要 `-` 参数），把每个文件都报为命中 | 提交前检查 | 改为 `paste -sd'|' -`，拒绝空模式 |

## 可以照搬到真实项目的经验
1. 先写强 thesis，让 falsifier 去削弱它；被驳倒的行要保留（C1、C5、C7）。
2. 在写约束之前先写每个 gadget 的 SPEC，并在小域上对**真实的构建代码**做穷举审计：随机测试和"生成器会拒绝"式
   的测试都找不到缺失的约束。
3. 测 Fiat–Shamir 敏感性时要固定 prover 的消息，并检查每一个挑战（包括子协议的）；库的默认行为（新开 transcript）
   并不是中性的选择。
4. 在同一个后端、同一个单位下比较不同写法；查找表会占用行，所以一定要检查范围的小端。
5. 攻击主张所量化范围的边界（这里是 k = 64、k = 4、c = 16、n = 16），而不是已经测过的点。
6. 请数据审计员把每个印出来的区间与主张的定义域逐一核对——k = 64 的点两次混进了"16 ≤ k ≤ 63"。
7. 每次回环（P6 → P5、P8 → P7）之后都重新跑门禁；`gate-check.log` 会保留历史。

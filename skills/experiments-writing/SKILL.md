---
name: experiments-writing
description: Write or revise a ZK evaluation section from recorded evidence. Plans results by the question each experiment answers, separates measured and theoretical costs, and checks provenance, comparison scope, attribution and limitations.
---

# Experiments writing

Use [clear exposition and contribution emphasis](../paper-playbook/references/clear-exposition.md):
connect the question to the measured object, observation and supported conclusion.
Split unrelated explanations and retain a bridge when changing the cost or scope.
Charge routine protocol work even when it is not emphasized as a contribution.

## Inputs and planning

Read the accepted contribution/evaluation claims, frozen logs and EVIDENCE rows,
implementation scope, baseline manifest, and parameter/security records. Use
[section planning](../paper-playbook/references/section-planning.md) and the
[evaluation outline](../paper-playbook/sections/10_experiments.md). For structural
examples, consult [the source analysis](../paper-playbook/references/formal-section-patterns.md).
Reference papers illustrate exposition; they do not validate our comparisons or
require us to reproduce their claims. Use the
[shared terminology rules](../paper-playbook/references/terminology.md).

Before drafting, map each intended result to
`question | object/configuration | metric and included work | evidence | conclusion | limit`.
An existing section plan can hold this map. Select tables and paragraphs that
answer these questions; no fixed table set, nine-part structure or positive result
is required. A cost-only paper may need analysis rather than experiments.

## Workflow

1. Obtain the final data and provenance from the experimenter. Report missing
   evidence rather than filling cells or launching an unrequested benchmark.
2. Identify the implemented and measured object: component, recursive circuit,
   prover, final verifier or full system. Separate symbolic counts, measured
   counts, capacity upper bounds, predictions and runtime measurements.
3. State comparison conditions before results: same computation, each system's
   own sizes, parameter/security status, trust assumptions, platform, versions and
   timing boundaries. Give the concrete parameter choices here, using the symbols
   defined in the Preliminaries Notation subsection. A compact configuration table
   can map symbol, selected value, role, provenance and measured/count-only status;
   check the applicable mathematical conditions. Follow the
   [parameter-placement rule](../paper-playbook/sections/07_preliminaries.md#general-setting-and-the-notation-subsection).
   Clearly mark contextual or reported-only numbers.
4. Draft result paragraphs as question/context → scoped observation → evidence →
   interpretation and relevant limit. Use a phase breakdown or controlled ablation
   for a mechanism claim only if the evidence supports it; a failed prediction is
   a legitimate result. Do not assume components must be combined or one is necessary.
5. Generate tables and figures from the data underlying EVIDENCE. Captions identify
   units, configurations, error bars/statistics, timing exclusions and ratio direction.
   Use readable venue-compliant layout rather than automatically shrinking tables.
6. Run `crbench audit-tex paper/main.tex EVIDENCE.md`, inspect the actual output and
   fix unexplained mismatches. Check abstract/intro/conclusion reuse the same scoped
   results. Record the audit and change in the project's existing logs.

## Number and comparison discipline

- Every own printed numerical result has an EVIDENCE row, including counts,
  estimates and parameter-derived bounds. Hand-placed results use `% EV:<ID>`.
  Follow the evidence tool's explicit convention for cited values, mathematical
  constants or other non-result numbers; never use an exemption to hide a result.
- Freeze the actual data version. Measurements added later need new provenance;
  do not relabel an earlier run as checking changed inputs.
- For measured performance, report hardware, library/toolchain commits, threads,
  repetitions, statistic and uncertainty, and the actual correctness check. Follow
  [bench-protocol](../bench-protocol/SKILL.md): interleaved comparable arms, warm-up,
  isolation/lock, thread control and proof verification for each timed proof run.
  For a component that emits no proof, state its relevant validation instead.
- Time includes or excludes witness generation, compilation, setup, preprocessing,
  wrapping and final verification as explicitly stated. Report excluded costs
  separately when relevant. State amortisation assumptions; do not silently divide
  setup cost over hypothetical future use.
- Equal-security comparisons require compatible security notions, level definitions,
  models and proven/conjectured regimes. A nominal security parameter is not a
  measured or proved security level. If unquantified, label that limitation and
  restrict comparisons to what remains meaningful.
- A runtime ratio needs compatible workloads, hardware and pipeline boundaries.
  A theoretical operation-count ratio needs compatible counted operations and
  scope; keep distinct trust interfaces distinct. Mark incomparable rows rather
  than computing a speedup. Use [baseline-pin](../baseline-pin/SKILL.md) for baseline
  fairness, and explain material differences or missing strongest comparators.
- Counts from different arithmetisations are not a common unit. A component saving
  does not establish a total-runtime saving; fewer group calls do not automatically
  outweigh added field, hashing, memory or setup work.
- State controlled changes before attributing improvement. A breakdown locates
  cost; it does not alone establish causality. Parallelisation may benefit methods
  differently; do not claim that single-threaded runs make hardware irrelevant.
- Keep timeouts, failed verification, exclusions and regimes where the method loses
  visible. Do not discard failed runs silently or generalise beyond tested inputs.

## Table choices (use only applicable rows)

| Reader need | Useful fields | Interpretation boundary |
|---|---|---|
| Know the configuration | Workload, field/curve, backend, algorithm parameters, security status | A security claim must trace to an actual bound; unknown is not a nominal bit count |
| Compare outcomes | Metric, scope, baseline, uncertainty, ratio direction | Mark measured versus reported; no unsupported ratio |
| Understand costs | Prover/verifier time, proof size, memory, setup/preprocessing as relevant | Do not hide a material adverse metric |
| Test the mechanism | Phase work, controlled ablation, prediction versus observation | Report which factors were actually controlled |
| Inspect scaling | Size/arity/degree or other varied factor with fixed factors specified | Avoid extrapolating past tested or defined regimes |
| Reproduce results | Versions, commands, artifact/data locations and verification | Instructions and actual executed runs remain distinguishable |

## Output

The requested evaluation text, generated tables/figures as needed, a compact
question-to-evidence plan and the actual audit result in existing project records.
Normally the text is `paper/sections/experiments.tex`; respect the manuscript's
existing organisation. Missing evidence is a research task, not an invitation to
invent prose, a theorem or an experiment.

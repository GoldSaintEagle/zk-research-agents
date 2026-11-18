# 10 Implementation and evaluation

## Reader question and inputs

What evidence answers the paper's performance or implementation questions, under
what conditions, and what can it not establish? Use frozen EVIDENCE rows and actual
logs, implementation scope, baseline manifests and the parameter/security record.
The writer reports results; missing experiments go back to the experimenter.

Use [section planning](../references/section-planning.md) and the
[reference analysis](../references/formal-section-patterns.md). Nova separates IVC
from compression measurements; KiloNova separates theoretical comparisons from its
prototype; Quasar explicitly limits its evaluation to components. These are useful
scope distinctions, not endorsements of their experimental claims.

## Functional outline

| Function | Content | Reader dependency |
|---|---|---|
| State the question and scope | Hypothesis being tested, implemented subset and metrics | What a result could establish |
| Make the comparison interpretable | Baselines, workloads, configurations, units, assumptions and excluded stages | Meaning of each row and ratio |
| Explain the method | Platform, versions, measurement protocol, repetitions, statistics and verification | Trust and reproducibility of the evidence |
| Present the result | Table/figure plus a factual scoped observation | Answer to the stated question |
| Explain the mechanism | Measured phase breakdown, ablation or model comparison when available | Strength and limits of causal attribution |
| State the trade-off and limit | Added work, unsupported regimes, failures and missing integration | What does not follow from the result |

Merge or reorder these functions as the experiment requires. A theory-only cost
analysis may have no implementation section. Do not invent nine subsections,
end-to-end timing, a mandatory positive ablation or a numeric security level.

## Evidence and comparison requirements

Follow [experiments-writing](../../experiments-writing/SKILL.md) for drafting,
[bench-protocol](../../bench-protocol/SKILL.md) for measurement and
[baseline-pin](../../baseline-pin/SKILL.md) for fair baselines.

- Give concrete instantiation choices here, mapping each value to its symbol
  from the Preliminaries Notation subsection. Identify the measured/count-only
  configuration and verify its admissibility conditions; see the
  [parameter-placement rule](07_preliminaries.md#general-setting-and-the-notation-subsection).
- State timing boundaries: witness generation, preprocessing, setup, compilation,
  recursion/wrapping, final verification and amortisation where applicable.
- Distinguish measured runtime, compiler constraint counts, symbolic operation
  counts, constructive upper bounds and estimates. Give each system its own size
  units; unlike arithmetisations are not interchangeable constraint units.
- A ratio needs compatible statements, security/trust assumptions, hardware and
  included work. Mark contextual or reported-only results and do not compute an
  unsupported speedup. If numerical security is unestablished, say so rather than
  filling a required-looking security column with a nominal parameter.
- Describe changes to the whole pipeline before attributing a gain to one step.
  A breakdown suggests where cost occurs; a suitable controlled ablation can test
  causality. Neither automatically proves a component is necessary.
- Show relevant costs and regimes where the result loses. Failed verification,
  timeouts and exclusions stay visible; do not silently discard them.
- Each own number maps to EVIDENCE, and tables/figures use the same source data.
  A component result does not imply a full-system improvement.

## Checklist

- [ ] Each result answers a stated question within the implemented/measured scope.
- [ ] Configurations, baselines, timing boundaries and security status are explicit.
- [ ] Actual protocol, statistics and correctness checks are reported accurately.
- [ ] Ratios and causal explanations have supporting evidence; added costs remain.
- [ ] Numbers are traceable and the numerical audit passes.

---
name: paper-playbook
description: Use when drafting or restructuring a ZK paper (protocol, system or application) for IACR or security venues: skeleton, page budget per paper type, and the moves of every section (preliminaries, protocol boxes, completeness / knowledge soundness / ZK / concrete soundness), with toy examples.
---

# Paper playbook

Use a section's purpose and the actual results to choose its structure. A reference
paper illustrates a possible exposition; it does not supply missing results or a
mandatory sequence of headings. For a language-only pass use
[polish-writing](../polish-writing/SKILL.md) without rebuilding the whole outline.

## Shared method

Apply [clear exposition and contribution emphasis](references/clear-exposition.md)
throughout: one main question per sentence, explicit links between transformations,
and new results distinguished from routine protocol steps. Read this guide when
drafting, restructuring or repairing a confusing technical explanation.

1. Read STATE and the requested section, its surrounding dependencies, accepted
   CLAIMS, relevant THEORY/CIRCUITS records, EVIDENCE and LITERATURE. Work within
   the requested scope; modifying a writing skill does not authorize rewriting a paper.
2. For a new or substantially restructured section, use
   [section planning](references/section-planning.md): inspect relevant reference
   passages; record what each paragraph/argument unit says, why it is there, what
   it presupposes and what the next unit needs from it. Analyse individual
   sentences when first-use definitions or transitions are the issue.
3. Build a short functional outline before prose, linking each intended result to
   its evidence and each unfamiliar object to an explanation before use. Merge,
   split or omit functions to fit the actual contribution. Do not force an open
   problem, framework, Insight, equation, figure or experiment into every paper.
4. Prefer semantically equivalent terms shared across the relevant independent
   papers consulted, prioritising published versions. Follow
   [terminology and source selection](references/terminology.md). A name occurring
   in one influential paper is not automatically standard. Explain a rare object's
   role before relying on its name; preserve genuinely different definitions.
   For symbols, prefer the notation of directly relevant prior papers, especially
   the primary baseline when definitions match. Use a coherent convention, avoid
   unnecessary renaming, and record any necessary change and source-to-paper mapping
   under [notation alignment](references/terminology.md#align-notation-with-prior-work-and-the-baseline).
5. Draft and check the chosen section using its guide below. Continue from plan to
   authorized prose without an extra approval stop unless the user requested one.
6. Recheck the edited text against its source claims and neighboring sections.
   Run evidence/LaTeX checks for manuscript changes, then follow the project's
   independent review workflow. A writing review does not replace scientific audits.

## Evidence and scope invariants

- Titles lead with the strongest established result or property, rather than only
  the problem being studied. Forms such as “Efficient …” or “… with Constant …”
  require the corresponding scoped evidence; follow the
  [result-oriented title guide](sections/01_title.md#lead-with-the-established-result).
- Our scientific statements enter the manuscript only from survived CLAIMS or the
  exact weakened wording. A desired paragraph is no reason to invent a theorem.
- Our numerical results trace to EVIDENCE. Distinguish measured data, operation
  counts, estimates, constructive bounds and figures quoted from a source. Keep
  numerical parameters, cost units and comparison conditions consistent.
- Theorem statements retain their notion, quantifiers, model, setup, assumptions
  and bounds. A component result does not establish a whole SNARK, ZK, numerical
  security or total-runtime improvement. Explicitly mark unproved properties.
- Unless a proof is short and straightforward, put its complete formal proof in
  the corresponding appendix. Keep the full theorem statement, material hypotheses
  and a concise, explicitly labelled proof sketch in the body, followed by an exact
  appendix reference. Follow the [proof-placement rule](sections/09_security_correctness.md#proof-placement)
  and applicable venue requirements; moving a proof never discharges its obligation.
- Start Preliminaries with a dedicated **Notation** subsection and a symbolic
  general setting. Give concrete evaluation parameter choices in the evaluation
  section, while retaining mathematical admissibility conditions and the supported
  theorem domain. Follow the [preliminaries placement rule](sections/07_preliminaries.md#general-setting-and-the-notation-subsection).
- For material limitations, explain the useful setting that remains and give an
  evidence-based applicability justification or a conditional mitigation, with
  its prerequisites and costs. Follow [limitations and applicability](references/limitations-and-applicability.md);
  do not invent a workaround or a practical guarantee to defend the contribution.
- Keep source observations separate from writing recommendations. Use public
  metadata and paraphrased examples, not private manuscript material, in this toolkit.

## Section guides (read only the relevant ones)

| Guide | Function |
|---|---|
| [Overall structure](sections/00_overall_structure.md) | Choose the paper's dependency order and a venue-specific page budget. |
| [Title](sections/01_title.md) | Foreground the established result/property and its object, preserving material scope. |
| [Abstract](sections/02_abstract.md) | Plan sentence functions and first-use dependencies. |
| [Introduction](sections/03_introduction.md) | Establish task, obstacle, contribution and scope. |
| [Contributions](sections/04_contributions.md) | State distinct supported results and where they are established. |
| [Technique overview](sections/05_technique_overview.md) | Explain how concrete operations solve the stated difficulty. |
| [Related work](sections/06_related_work.md) | Compare compatible objects and position the actual difference. |
| [Preliminaries](sections/07_preliminaries.md) | Establish Notation and general definitions/interfaces; defer concrete evaluation parameters. |
| [Construction](sections/08_main_construction.md) | Specify objects, algorithms, checks and their composition. |
| [Security and correctness](sections/09_security_correctness.md) | Make claims, hypotheses and proof dependencies explicit. |
| [Evaluation](sections/10_experiments.md) | Answer supported evaluation questions with scoped evidence. |
| [Conclusion](sections/11_conclusion.md) | State what the established results permit the reader to conclude. |
| [Appendix](sections/12_appendix.md) | Locate full proofs, extra evidence and reproducibility details. |

## Source examples and specialist skills

Read the [source/version register](references/source-corpus.md) before reusing the
[front-section examples](references/front-section-patterns.md) or
[formal/evaluation examples](references/formal-section-patterns.md). These document
selected actual passages from Nova, HyperNova, Quasar and KiloNova, not a universal
template or a survey establishing majority terminology.

Use [abstract-craft](../abstract-craft/SKILL.md),
[technique-overview](../technique-overview/SKILL.md),
[related-work-writing](../related-work-writing/SKILL.md) and
[experiments-writing](../experiments-writing/SKILL.md) for their respective sections.
Use the project's definitions, compilation, soundness and circuit audit records;
writing guidance never overrides their mathematical requirements.

Synthetic examples in `examples/` illustrate decisions, not scientific results:
[introduction/contributions](examples/toy_intro_and_contributions.md),
[overview/related work](examples/toy_overview_and_related.md),
[security/evaluation](examples/toy_security_and_eval.md), and
[abstracts](examples/toy_abstracts.md). Do not import their numbers or claims.

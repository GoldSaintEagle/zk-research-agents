# Source examples for introductory sections

Use this reference when choosing an introduction, contribution, overview or
related-work structure. The units below are selected paragraphs or argument
units, not a claim to have audited the papers' proofs or experiments. Page numbers
are PDF page numbers in the inspected versions. See [source corpus](source-corpus.md)
for version/status details and [section planning](section-planning.md) for adapting
the method to a new manuscript. Published Nova is the proceedings text; HyperNova
locators below refer to its extended version. Quasar and KiloNova are preprints.

## Nova: primitive, construction, evidence, comparison

Source: [published CRYPTO 2022 paper](https://crypto.iacr.org/2022/papers/538806_1_En_13_Chapter_OnlinePDF.pdf).

| Location and unit | Content | Function and dependency |
|---|---|---|
| §1, pp1–2, opening paragraphs | IVC, applications and prior recursive approaches | Establishes the task before the proposed primitive. |
| §1, p2, new-approach paragraph | Defers checking instances | Connects the limitation to the proposed change. |
| §1.1, p2, definition paragraph | Parties, instances, witnesses and folded output | Supplies the interface before the security intuition. |
| §1.1, p3, relaxed-R1CS discussion and Theorem 1 | Relation choice, guarantee and costs | Turns the idea into a qualified result. |
| §1.2, pp3–4 | IVC construction, running instance and compression | Explains composition after the primitive. |
| §§1.3–1.4, pp5–8 | Evaluation, comparison and concurrent work | Separates measured evidence, technical positioning and version timing. |

The definition paragraph supplies inputs, then outputs, then an informal guarantee.
That order prevents a new name from carrying unexplained content. Theorems in the
introduction demonstrate that contribution statements need not forbid theorem
pointers. This structure does not require a separate contribution list.

## HyperNova: contextualised difficulties and corresponding mechanisms

Source: [extended version](https://eprint.iacr.org/2023/573), associated with
[CRYPTO 2024](https://link.springer.com/chapter/10.1007/978-3-031-68403-6_11).

| Location and unit | Content | Function and dependency |
|---|---|---|
| §§1–1.1, pp4–5 | IVC and Nova's approach | Supplies the baseline needed for the limitations. |
| §1.2, pp5–7, four problem groups | High-degree constraints, instruction-dependent costs, privacy and curve cycles | Explains each target before naming a solution. |
| §1.3(1), pp7–8 | Generalised folding interface and sumcheck-derived relation | Introduces objects before explaining their use. |
| §1.3(1), p8, early-stopping discussion | A reduction alone leaves a folding obligation | Distinguishes an intermediate step from the desired primitive. |
| §1.3(2–4), pp9–11 | Non-uniform recursion, randomisation and curve instantiation | Connects mechanisms to previously stated targets. |
| §1.4, p11 onward | Later results | Separates subsequent developments from the original comparison. |

The numbered correspondence works because this version actually states several
distinct problems. It does not make open-question framing mandatory for other
papers. Extended-version section order is not asserted to match the proceedings.

## Quasar: a cost boundary and an explanatory unsuccessful attempt

Source: [public preprint](https://eprint.iacr.org/2025/1912); inspected 55-page copy.

| Location and unit | Content | Function and dependency |
|---|---|---|
| §1, pp1–2 | Large computations, recursion and accumulation | Narrows application context to a per-step cost. |
| §1.1, pp2–3 | Recursion overhead and commitment combinations | Defines the measured operation before the target. |
| §1.2, pp3–4 | Reduction, composition and application | Orders deliverables by what each construction needs. |
| §§1.3–1.4, pp4–6 | Cost categories and evaluation scope | Keeps selected-operation gains distinct from system throughput. |
| §2.1, p7, baseline and unsuccessful attempt | Evaluation checking retains a commitment list | Shows why a local change leaves a recursive obligation. |
| §2.1, pp7–8, union-polynomial paragraphs | Partial evaluation and checked values | Introduces the concrete operation before naming the primitive. |
| Appendix B, pp37–38 | Recursion, accumulation, folding and preprocessing families | Groups work by technical role rather than one forced axis. |

The unsuccessful attempt is useful because it identifies what survives into the
next step. Its presence does not justify inventing one in every overview.

## KiloNova: background followed by a component chain

Source: [public preprint](https://eprint.iacr.org/2023/1579), *Machine Executions*;
inspected 50-page copy.

| Location and unit | Content | Function and dependency |
|---|---|---|
| §1, pp1–3 | Machine execution, incremental computation and non-uniformity | Establishes the setting before the index-folding problem. |
| §2 opening, p3 and Figure 1 | Component map and reused compiler | Announces dependencies and distinguishes adopted material. |
| §2.1, pp3–5 | Relations, indices, instances and prior reductions | Supplies objects used by the later technique. |
| §2.2, pp5–7 | Direct folding's difficulties, modified relation and encoded index | Connects each change to an identified obstacle. |
| §§2.3–2.4, pp7–10 | PCD followed by final preprocessing argument | Explains how outputs of one stage serve the next. |
| Appendix A, pp34–36 | Machine-execution methods and folding comparisons | Separates application-level comparison from primitive-level comparison. |

The actual component chain explains the section order. A new paper with only a
component result must stop at that component; it cannot borrow the final compiler
or stronger system guarantee to complete the same outline.

## Reusable planning choices

- **Introduction:** familiar task → necessary background → specific obstacle →
  actual response → scoped consequence. Start at the obstacle if the task is
  already familiar; expand the background when it is not.
- **Contributions:** result → concrete difference → material conditions → supporting
  location. Select the number and order from the accepted deliverables.
- **Overview:** objects → obstacle → operation → validity intuition → actual
  composition → cost/limit. Repeat only for mechanisms the paper contains.
- **Related work:** comparison question → source-checked approaches → precise
  relationship and scope. Use tables or historical order when they clarify it.

These are writing functions, not evidence of majority terminology or correctness
of the reference papers. Follow [terminology](terminology.md) for naming choices.
Do not reproduce promotional adjectives, unsupported comparisons or private
material merely because a reference supplies a convenient narrative.

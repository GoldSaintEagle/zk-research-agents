# 02 Abstract — order information by reader dependencies

Follow [abstract-craft](../../abstract-craft/SKILL.md), including its
[sentence-by-sentence Quasar/KiloNova analysis](../../abstract-craft/references/sentence-functions.md).
Those abstracts illustrate two entry points: a concrete computational bottleneck,
or an application problem narrowed to a technical gap. They do not establish a
mandatory paragraph/sentence count or lend their technical claims to another paper.

## Outline

| Move | Content |
|---|---|
| Context and object | State the task and familiar mathematical/computational objects. |
| Problem | Identify the operation, limitation and cost unit; explain unfamiliar terms needed to understand it. |
| Contribution | Name the kind of result and its scope; a new scheme name is optional. |
| Mechanism | Explain concrete actions and their role before relying on an unfamiliar label. |
| Guarantee/composition | Follow the actual construction chain; retain theorem premises and bounds. |
| Evidence/trade-off | Give scope and baseline, distinguish counts from measurements, and state material added costs. |
| Consequence | State only what the result supports; artifact or formalisation belongs here only if available and useful. |

This is a flexible order of functions. Two or three paragraphs may group context,
technique and results, but no paragraph quota is required. Do not force a claimed
open problem, a new “viewpoint”, prior-paper venue/year citations, an experimental
range or a final SNARK into a paper that does not support them. If unification is
actually claimed, state which earlier methods are covered and under what parameters.

## Checks

- Follow [clear exposition](../references/clear-exposition.md): separate the target
  operation, its algebraic reduction and subsequent implementation obstacle.
  Each non-obvious step needs a concrete connecting explanation. Routine
  Fiat–Shamir and commitment-before-challenge order are not headline contributions.

- Create `paper/ABSTRACT_PLAN.md` before prose, with each sentence's function,
  prerequisites, concrete content, claim/evidence and material boundary.
- Prefer terms shared by relevant independent papers. A reference-specific name
  needs its role explained; a single citation does not make it familiar.
- State the actual security model and additional assumptions. Do not imply
  negligible error, numerical security, succinctness or zero knowledge without the
  supporting theorem. Keep fixed-hash assumptions distinct from ideal-oracle proofs.
- Put configuration and comparator before performance numbers; every own number
  has an EVIDENCE row. Do not infer total speed from a component or selected counts.
- Keep abstract, contribution list and conclusion consistent in substance. Useful
  reordering is permitted; claim strengthening is not.
- Respect the actual venue and submission-form limits. Compile and inspect page 1
  with the title and keywords. Shorten prose without changing template geometry,
  font sizes or adding negative spacing to force a fit.

## Plain-text form

Generate `paper/abstract_plain.txt` from the same prose, without TeX commands,
evidence comments, PDF hyphenation or ligature artifacts. Compare it with the LaTeX
abstract and synchronize any submission-form copy. The plain-text version retains
all assumptions, scope qualifiers and numerical values.

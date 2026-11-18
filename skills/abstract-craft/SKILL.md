---
name: abstract-craft
description: Use when writing or revising a research-paper abstract and its plain-text submission twin. Plans each sentence by its function and information dependencies, uses source-checked reference abstracts as structural examples, and checks terminology, theorem scope, evidence and comparison boundaries.
---

# Abstract craft

## Inputs

Read the contribution list and actual construction, theorem premises, evaluation
and conclusion. Use `CLAIMS.md` survived/weakened rows and `EVIDENCE.md` for our
results; weakened rows retain their restricted wording. Read user-named reference
abstracts in their actual versions rather than reconstructing them from memory.

## Structure before prose

An abstract must let a reader understand the task before asking them to understand
our mechanism. Start from a familiar object and a specific problem, identify the
kind of contribution, explain the operative idea, and state supported results with
their conditions. A framework name or a sentence of the form “we view X as Y” is
optional; neither substitutes for explaining the work.

Apply [clear exposition and contribution emphasis](../paper-playbook/references/clear-exposition.md).
Give each sentence one main question unless the combined points are simple and
immediately related. Establish the operation, explain the essential transformation,
then introduce an obstacle created by that transformation. For commitment checks,
identify the random linear combination first, then explain how the chosen method
encodes the group relation in polynomial checks; only afterward discuss recursive
field arithmetic if needed. “Uses polynomials” alone does not explain the reduction.
Routine commitment-before-challenge order and Fiat–Shamir are background steps,
not headline contributions. Spend the mechanism sentence on the actual new delta;
retain any material additional security assumptions.

Use [the Quasar/KiloNova sentence-function analysis and reusable outline](references/sentence-functions.md)
when planning or restructuring an abstract. It distinguishes two observed routes:
start at a measurable bottleneck, or narrow from an application to a precise gap.
These are examples of rhetorical structure, not authorities for our security or
performance claims and not a survey establishing field-wide terminology.

## Procedure

1. **Extract the actual result.** In working notes, write the task, concrete
   obstacle, contribution type, mechanism, guarantee, evidence and material cost.
   Do not invent an open problem, final compiler, experiment or artifact to fill a slot.
2. **Analyse requested references sentence by sentence.** Record the source/version,
   each sentence's content, its primary function, and the prerequisite it supplies
   for later sentences. Prefer relevant published versions where available; identify
   a preprint accurately. Distil the pattern rather than copying sentences or
   inheriting words such as “novel”, “optimal” or “state of the art”.
3. **Plan our sentences before drafting** in `paper/ABSTRACT_PLAN.md`:
   `sentence | function | prerequisites | concrete content | claim/evidence | boundary`.
   The user's request to rewrite authorizes producing the plan and prose; pause
   after the plan only if the user asks for a planning/approval stage.
4. **Draft in dependency order** using the table below. Merge or split functions
   as needed. Paragraph count and sentence count are not fixed; two or three
   paragraphs can separate context, technique and results when useful. Do not
   require an “open question” sentence or venue/year citations merely for form.
5. **Check terminology and first use.** Follow
   [the shared-usage terminology rules](../paper-playbook/references/terminology.md).
   A name found in one paper is not necessarily familiar. Before a rare object or
   acronym carries an argument, explain what it represents, proves or computes.
   Prefer a concrete description such as “check a linear combination of commitments”
   to a new label that leaves the operation unspecified. Use explicit antecedents:
   readers should know what “these coefficients” or “this reduction” refers to.
6. **Audit every result against its evidence.** Apply the checks below, then compare
   abstract, introduction and conclusion for the same objects, scope and numbers.
   A rhetorical rewrite may reorder results; it must not strengthen them.
7. **Deliver and verify.** Write the plain-text twin from the same prose. Compile,
   inspect the abstract page, check cross-references and run the numerical evidence
   audit. Follow the actual venue/submission-form limits; shorten redundant prose
   rather than changing fonts, margins or hiding material premises. Log the change
   and hand the revised text to an independent reviewer under the project workflow.

## Sentence-function outline

| Function | Reader's question | Required content |
|---|---|---|
| Context and object | What task is this about? | Familiar setting and the mathematical/computational objects involved; a focused bottleneck can supply the context. |
| Problem and scope | What specifically remains difficult here? | Operation, limitation and cost unit; define unfamiliar parameters. A local integration difficulty need not be a global open problem. |
| Contribution | What does this paper provide? | Construction, theorem, implementation or analysis, with its intended scope; a name is optional. |
| Mechanism | How does it address that difficulty? | Actions on concrete objects, their order and the connection to the problem; introduce unusual terms through their role. |
| Composition or guarantee | What follows, under what premises? | Actual component-to-system chain or precise theorem, including material model/knowledge assumptions. Omit nonexistent compilation steps. |
| Evidence and trade-off | What is proved, counted or measured? | Scope and baseline before comparison; benefit together with material added cost. |
| Consequence and limit | What can the reader conclude? | Supported significance and interpretation-changing limitations; artifact/formalisation only when available and useful. |

## Claim and evidence checks

- Every own numerical result maps to an EVIDENCE row, including a `% EV:E...`
  comment in LaTeX. State the configuration and comparison baseline. Distinguish
  exact operation counts, constructive upper bounds, estimates and measurements.
- State material security assumptions and the exact guarantee proved. When
  negligible error, numerical security, succinctness or zero knowledge is not
  established, do not imply it through the contribution's name. An additional
  knowledge assumption is not a theorem inherited from a reference paper.
- A comparative security/performance statement needs compatible premises and
  measurement scope. Component timings do not establish a full-system speedup;
  fewer selected operations do not establish lower total cost. Keep changed trust
  boundaries and important added costs beside the comparison.
- Do not force setup or post-quantum labels into an abstract about a component.
  If those properties are claimed, state the applicable setup/model/assumptions
  and check the actual theorem. Do not turn a plausible property into a proven one.
- Avoid unsupported “first”, “optimal”, “state of the art”, “practical”, “secure”
  or “significantly faster”. Replace them with the actual result. An existing
  paper's abstract is not evidence that the same description applies to ours.
- Preserve author terminology in quotations, but choose shared, semantically
  equivalent terminology for our own prose. Do not rename a distinct object to
  make it sound standard. Delete unnecessary acronyms and method names.
- A range's lower end is conservative and measured; label an estimated upper end.
  Do not mix configurations below the claimed security level or proven and
  conjectured regimes. Formalisation claims name exactly the checked core.

## Output

`paper/ABSTRACT_PLAN.md`, `paper/sections/abstract.tex`,
`paper/abstract_plain.txt`, and a short entry in `paper/CHANGELOG.md`.
Keep detailed reference-source analysis in research notes, not in the abstract.
Synchronize the submission-form copy and affected local manuscript build.

See also [the playbook abstract section](../paper-playbook/sections/02_abstract.md).

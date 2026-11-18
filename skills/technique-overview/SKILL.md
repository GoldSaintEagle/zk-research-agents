---
name: technique-overview
description: Draft or revise a technique overview by explaining concrete objects, obstacles, operations and composition dependencies. Uses checked reference passages as structural examples and preserves theorem assumptions, cost boundaries and established terminology.
---

# Technique overview

## Inputs and reader test

Read the actual construction, theorem statements and assumptions, survived/weakened
CLAIMS, EVIDENCE and checked original references. A reader should be able to restate
the core operation, identify what enters and leaves each component, and explain
which premise makes the informal argument valid. Plausibility does not establish
security; the overview must point to the real proofs.

For a substantial rewrite, use the shared
[section-planning method](../paper-playbook/references/section-planning.md) and
[source passage analyses](../paper-playbook/references/front-section-patterns.md).
The [overview section guide](../paper-playbook/sections/05_technique_overview.md)
gives its flexible outline. Read only the relevant examples and references.

Follow [clear exposition and contribution emphasis](../paper-playbook/references/clear-exposition.md).
Carry the reader through the actual objects A → B → C; explain each non-obvious
transformation before moving to the difficulty it creates. Split distinct problems
across sentences and signal independent branches. Explain how a group equation
becomes a polynomial relation when that is the method; naming a certificate is
not the intervening argument. Keep routine commitment/challenge order and standard
Fiat–Shamir compilation in their supporting role, preserving their real premises.

## Procedure

1. Extract the task, obstacle, actual change, required property and cost consequence
   from the body. Record which parts are new, adapted or reused. A theory result,
   component improvement and complete system require different explanations.
2. Inspect the requested references' relevant overview passages. In working notes,
   record the source/version, paragraph or argument unit, content, function and
   prerequisites. Analyse individual sentences where a new term or transition
   needs explanation. Borrow the functional pattern, not names or distinctive prose.
3. Plan our units before drafting: reader question → concrete objects → operation
   or obstacle → mechanism → validity intuition → interface/cost consequence.
   Merge or reorder units when dependencies permit. Questions, failed attempts,
   numbered Insights, a diagram and a worked example are optional devices.
4. Describe actions on objects before using unusual names. Follow the
   [shared-usage terminology rules](../paper-playbook/references/terminology.md):
   among equivalent names prefer those shared by most relevant independent works
   consulted, prioritising published sources. Attribute source-specific terminology
   and keep inequivalent definitions distinct.
5. Introduce premises before derivations. Reuse formulas from the body; label a
   simplified case and check the mapping rather than testing string equality alone.
   Explain what the equation checks and what remains to be proved or verified.
6. State composition only for actual components. Give each input/output interface
   and required property; name the theorem supporting the step. If using a PIOP,
   PCS and Fiat–Shamir compiler, state the required degree/query bounds, commitment
   properties and model. If the construction is a folding scheme or a circuit,
   describe that construction directly. Do not invent a final argument.
7. Connect each gain to its cost measure and material price. Distinguish native
   operations from in-circuit work, local verification from final verification,
   and a count from measured runtime. Preserve setup, public-input processing,
   preprocessing and memory boundaries where they affect the claim.
8. Check the draft against the body and its evidence. Request a figure only if it
   clarifies the mechanism. Under the project's review workflow, have an independent
   reader perform the restatement test and report missing prerequisites or scope
   mismatches; this editorial test does not replace scientific falsification.

## Common failure modes

- Treating two unrelated techniques as a unified framework because a template asks
  for two routes, or placing prior works at geometric corners without a proven map.
- Explaining a method through undefined labels instead of commitments, evaluations,
  messages, relations or circuits and the operations performed on them.
- Repeating the related-work survey instead of explaining the actual change.
- Assuming ROM security carries over to a chosen hash, or omitting an extra
  knowledge assumption when moving from a primitive to recursion.
- Adding an unproved extension, security level, final SNARK or performance claim
  because it makes the story sound more complete.

## Output

The requested section, commonly `paper/sections/overview.tex` or part of `intro.tex`,
its function/dependency plan in the project's section-planning notes, and a short
change log. Write a figure request to `paper/figs/REQUESTS.md` only when needed.
For manuscript edits, compile and run the applicable claim/numerical consistency
checks; do not run new experiments as part of a prose pass.

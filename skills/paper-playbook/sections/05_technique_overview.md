# 05 Technique overview

## Reader's question and inputs

What changes in the construction, why does it address the difficulty, and which
guarantees or obligations remain? Read the actual algorithms, theorem hypotheses,
accepted claim map and relevant original constructions. The overview should let a
reader restate the mechanism and its conditions before reading the formal details.
It is intuition and a map to proofs, not a replacement for them.

Use [section planning](../references/section-planning.md), the
[observed reference patterns](../references/front-section-patterns.md), and
[technique-overview](../../technique-overview/SKILL.md) for the full workflow.

## Functional outline

| Function | Content and dependency |
|---|---|
| Set up the relevant objects | Introduce the relation, instance, witness, commitment or circuit actually used by the idea. Define the local symbols. |
| Explain the obstacle | Show the operation or invariant that causes the difficulty. Recall only the prior construction needed for that explanation. |
| Present the change | Describe what is computed, committed, queried, reduced or deferred, and in what order. A useful identity or small example may expose the mechanism. |
| Account for validity | Explain informally why the checks imply the claimed relation, and point to the exact proof. State premises before drawing conclusions. |
| Compose when applicable | Identify what one component outputs and what the next requires; distinguish new, adapted and reused parts. |
| State costs and limits | Connect the mechanism to the same cost units as the theorem/evaluation, including work shifted to another stage and conditions of applicability. |

The sequence may repeat for independent mechanisms. An initial failed approach is
useful when it reveals a real obstruction, as in Quasar's commitment example; it
is not a requirement. HyperNova's problem/result pairing and KiloNova's component
chain are other options. Do not force two prior routes into a common object or
invent a question for each technique.

## Presentation decisions

- Use headings naming the actual operation, object or result. Neither numbered
  “Insights” nor full-sentence headings are required. Avoid headings that add a new
  term without explaining the action.
- Include formulas, diagrams or worked examples only when they resolve a reader
  dependency. A component/data-flow diagram often helps; a geometric diagram of
  prior works is appropriate only if its axes and claimed coverage are justified.
- Reuse body formulas and definitions. If simplifying notation or a special case,
  say so and check equivalence under the stated assumptions; literal string identity
  is not a mathematical correctness test.
- Describe the actual protocol layers. A folding scheme or circuit gadget need
  not be forced into a PIOP–PCS–Fiat–Shamir pipeline or a full SNARK.
- An extension belongs here only if an accepted result supports it. Do not add
  speculative applicability merely to increase perceived significance.

## Checklist

- [ ] A reader can explain the mechanism, its inputs/outputs and central premise.
- [ ] New names follow concrete explanations; symbols precede their first use.
- [ ] Every informal guarantee links to an actual result with matching assumptions.
- [ ] Composition interfaces and any shifted cost are explicit.
- [ ] Figures, equations and headings serve the argument rather than a quota.

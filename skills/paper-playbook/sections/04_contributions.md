# 04 Contributions

## Reader's question and inputs

What are the paper's distinct deliverables, and where are they justified? Start
from survived CLAIMS rows or the exact weakened wording, the actual theorem
statements, implementation scope and EVIDENCE. A contribution list summarises
these inputs; it does not create new results.

Follow [contribution emphasis](../references/clear-exposition.md): exclude ordinary
Fiat–Shamir, commitment-before-challenge ordering and other standard protocol
steps from the claimed novelty. For an integration, identify the precise new
property or benefit and its evidence. Use separate sentences for distinct results
whose premises need explanation; do not mix a routine step with a new theorem to
make the step sound novel.

Use [section planning](../references/section-planning.md) and the
[reference contribution patterns](../references/front-section-patterns.md).

## Functional outline

| Function | Content and prerequisite |
|---|---|
| Identify the result | State the construction, theorem, algorithm, implementation, analysis or negative finding in ordinary technical terms. The opening context must already explain its objects. |
| Explain the difference | Name the new operation, property or scope relative to the checked baseline. Do not assume a method name communicates the contribution. |
| State conditions and consequence | Include material premises, the exact notion established and any trade-off needed to interpret the result. |
| Provide a destination | Point to the relevant theorem, construction, section, figure or table. Choose the pointer that helps verify the claim. |

These functions can occupy one paragraph, several bullets, or subsections. Use
dependency order for a primitive followed by a compiler or application; group
independent results by importance or theme. A single main result does not need
three additional bullets. Theory-only work does not need an implementation claim.

## Wording and scope

- Choose verbs by evidence, not a ranking of rhetorical force: prove a theorem,
  construct a scheme, implement a component, measure a runtime, or analyse a
  limitation. Do not replace an accurate modest verb with a stronger one.
- Explain the result before its pointer. Theorem references are useful and allowed;
  a list consisting only of theorem numbers is uninformative.
- Conditions and necessary trade-offs belong beside the affected contribution.
  Do not remove them to make the contribution list sound stronger. Detailed
  qualification can be elsewhere when the short statement remains accurate.
- Explain why a restricted result still matters in a concrete supported setting.
  Follow [limitations and applicability](../references/limitations-and-applicability.md):
  state the workload mapping, any mitigation and its price, and distinguish
  established applicability from a proposed extension. Do not guarantee relevance
  by asserting that arbitrary computations fit an unproved transformation.
- Put numbers where they support the corresponding deliverable, with EVIDENCE
  and comparison scope. There is no rule restricting numbers to selected bullets.
- A claim of subsuming prior methods needs an actual correspondence under stated
  hypotheses. Do not require a unified framework, coverage percentage, optimal
  selection rule or final SNARK when the paper establishes none.
- Keep costs and security properties distinct. Operation counts are not total
  runtime; a component is not a complete recursive system; an extra knowledge
  assumption is not an inherited theorem. Attribute reused components.
- Use established terms shared by relevant independent literature where their
  definitions match. A name can be retained for a genuinely distinct recurring
  concept, with its role explained before it carries the argument.

## Checklist

- [ ] Every deliverable has an accepted claim and an exact supporting location.
- [ ] Distinct contributions are not repeated under new names.
- [ ] Assumptions, comparison boundaries and necessary costs remain visible.
- [ ] Number and order of items follow the actual results, not a fixed template.
- [ ] Abstract, contribution statements and conclusion make compatible claims.

See [the synthetic examples](../examples/toy_intro_and_contributions.md).

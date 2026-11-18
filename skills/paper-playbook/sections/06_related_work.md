# 06 Related work

## Reader's question and inputs

Which prior results address the relevant task, how do their definitions and
guarantees differ, and what is the precise contribution here? Use the checked
`LITERATURE.md` matrix, verified bibliography, original passages and our accepted
results. Read [section planning](../references/section-planning.md),
[reference positioning patterns](../references/front-section-patterns.md), and
[related-work-writing](../../related-work-writing/SKILL.md).

## Functional outline

| Function | Content and dependency |
|---|---|
| Establish comparison scope | Identify the task, object, model or cost being compared before grouping papers. |
| Explain relevant approaches | Summarise the mechanism and supported result of each necessary work or family. Give actual sources and avoid unsupported claims about all prior work. |
| State the relationship | Explain a precise difference, restriction, shared technique or complementary role, under the relevant assumptions. |
| Compare when valid | Use common definitions and cost units; provide a table when it clarifies several comparable properties. Label mismatches and unavailable entries. |
| Position this paper | State the supported delta and retained limitations. Point to the full contribution or proof instead of repeating it. |
| Handle timing when relevant | Distinguish prior, concurrent and subsequent work using the actual versions and dates. |

Group by the question that matters: computational model, supported relations,
proof notion, recursion method, setup, commitment interface or cost. Chronology
is useful when explaining a development, but a chronological catalogue alone
does not establish a contribution. No fixed pair of axes, contrasting verbs,
bridge paragraph, five-sentence pitch or mandatory “Ours” row is required.

## Source and comparison discipline

- Prefer relevant published sources and inspect the actual technical passage.
  If a detail comes from an extended version or preprint, identify that version.
  A later paper's description is not a substitute for reading the cited original.
- For claimed bottlenecks, inspect the original analysis or evaluation. Do not
  automatically turn a measured cost on one workload into an inherent limitation.
- Map equivalent terms into common prose under the
  [terminology rules](../references/terminology.md); preserve different definitions,
  trust boundaries and security notions. Similar names do not imply the same scheme.
- Compare the strongest relevant alternatives, including complementary results.
  Not every prior approach must lose or occupy a boundary of our construction.
- Separate source-reported measurements, our reruns, estimates and asymptotic
  analysis. Incomparable security levels or statements cannot support a speedup.
- Cite own previous work in the same manner as other work, subject to venue rules.
  State factual differences without disparagement or invented shortcomings.

## Checklist

- [ ] Each characterisation has a source/version and technical locator in working notes.
- [ ] Grouping follows the paper's question; no artificial unification is asserted.
- [ ] Comparative entries share scope or clearly disclose their differences.
- [ ] Our positioning agrees with the exact accepted claims and evidence.
- [ ] Publication status, concurrent work and source-specific vocabulary are accurate.

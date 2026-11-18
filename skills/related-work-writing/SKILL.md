---
name: related-work-writing
description: Draft or audit related work using original sources, comparison scope and paragraph functions. Explains technical relationships without forced axes or unification, preserves definition and security differences, and uses tables when the evidence supports comparison.
---

# Related-work writing

Use [clear exposition and contribution emphasis](../paper-playbook/references/clear-exposition.md):
keep each comparison focused, connect successive technical differences, and
attribute standard ingredients before identifying the supported new result.
Routine use of a commitment or Fiat–Shamir is not itself a novelty distinction.

## Inputs

Read `LITERATURE.md`, the verified `refs.bib`, the paper's actual task and accepted
contributions, and the original passages supporting technical comparisons. An
objective equation or framework is not required. Use
[section planning](../paper-playbook/references/section-planning.md),
[the section guide](../paper-playbook/sections/06_related_work.md), and
[reference passage analyses](../paper-playbook/references/front-section-patterns.md)
when planning or restructuring the section.

## Procedure

1. Define what is being compared: computation, relation, proof notion, recursion
   method, trust model, setup or cost. Identify closest competitors and genuinely
   complementary work. Do not select categories to make our row uniquely favourable.
2. For each substantive description, inspect the original definition, theorem,
   algorithm or experiment. Record source/version and exact locator in working
   notes. A published version takes priority when it contains the relevant detail;
   identify extended/preprint-only details separately. Do not upgrade publication
   status or use a blog's paraphrase as proof of a technical result.
3. Analyse relevant reference paragraphs by content, role and dependency. Choose
   a grouping that explains the differences: e.g. model, supported relation,
   commitment interface or proof-composition method. One or two axes can help but
   are not mandatory. Chronology can explain development when that is the point.
4. Plan paragraphs as comparison scope → approach and supported result → relation
   to the present task. A source-specific distinction may require its own paragraph;
   unrelated work need not be forced into one cost model. Avoid a catalogue of
   summaries without explaining relevance.
5. Apply the [shared-usage terminology rules](../paper-playbook/references/terminology.md).
   Verify semantic equivalence before normalising terms; prefer usage shared by
   most relevant independent works consulted, prioritising published work. One
   paper's unusual label is not a field convention. Explain and attribute distinct
   definitions rather than renaming them to resemble ours.
6. Add a comparison table when several properties or systems need parallel
   inspection. Include an “Ours” row if comparable; its location and emphasis are
   editorial choices. Use the table discipline below. A short precise paragraph
   is sufficient for a small or mostly qualitative comparison.
7. State our supported difference with its premises and cost. Not every prior
   work must have a defect, and complementary methods may be better for another
   objective. Do not claim that all earlier methods are special cases unless an
   actual correspondence is established. Cross-reference the contribution instead
   of repeating a fixed elevator pitch.
8. Check coverage against the existing literature search and the task's freshness
   needs. Route missing or stale searches to `lit-scout`; distinguish concurrent
   and subsequent versions by dates. Grey literature may supply leads or public
   implementation facts, but identify its status and retain primary technical
   sources where available. Keep bibliography verification with `bib-verify`.

## Comparison-table discipline

Select columns that answer the question. Possible columns are relation/setting,
setup and assumptions, guarantee, prover work, verifier work, proof size, recursion
cost, preprocessing and memory. A component comparison need not fill a full-SNARK
table or claim post-quantum security.

- Define parameters and units in the caption; state whether costs are per step,
  amortised, online, recursive or final. Native and in-circuit operations are
  different measures. Translate notation only after checking the definitions.
- Distinguish formulas, estimates, source-reported measurements and our reruns.
  Our printed numerical results need EVIDENCE rows; cited source numbers need
  precise provenance and the project's applicable audit annotations.
- Compare the same task and compatible security premises before reporting ratios.
  Mark unavailable or incomparable entries as such and explain why. Do not silently
  combine different hardware, security levels, trust boundaries or circuit encodings.
- Retain proven/conjectured/heuristic status, knowledge assumptions and setup
  distinctions. A universal SRS is not transparent; a hash-based construction is
  not automatically proven post-quantum; soundness is not knowledge soundness.
- Keep our entries consistent with the body and abstract under the same
  configuration. Symbolic simplifications need a checked equivalence, not merely
  matching strings.

## Tone and attribution

Use factual descriptions of assumptions, supported settings and measured costs.
Avoid disparagement, unsubstantiated “first/best” claims and invented shortcomings.
Inspect an earlier work's own analysis or experiments before attributing a
bottleneck to it. Cite the authors' earlier papers consistently with other work
and the venue's anonymity policy. Do not copy distinctive wording or import a
reference's evaluation of its competitors as an independently verified fact.

## Output and checks

Write the requested section, commonly `paper/sections/related.tex` or part of
`intro.tex`, and a table only if useful. Keep source/version/locator and
definition-mapping notes in `LITERATURE.md` or its linked research notes.

- [ ] Every substantive comparison has an inspected primary source.
- [ ] Grouping and scope explain relevance without forcing a superiority narrative.
- [ ] Source versions, guarantees, units and trust boundaries remain distinct.
- [ ] Our statements use accepted claims and properly scoped evidence.
- [ ] The section uses familiar terms where definitions match and attributes exceptions.

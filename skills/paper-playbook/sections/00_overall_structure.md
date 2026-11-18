# 00 Overall structure and page planning

## Choose a dependency order

Use [section planning](../references/section-planning.md) to map the actual results
to reader questions before selecting headings. Read the relevant
[source examples](../references/source-corpus.md); a source's layout is one option,
not the template all papers must follow.

| Function | What it supplies | Placement options |
|---|---|---|
| Motivation and positioning | Task, concrete difficulty and supported contributions | Introduction; detailed related work can be separate. |
| Informal mechanism | Operations and the reason they address the difficulty | End of introduction or a separate overview. |
| Definitions and interfaces | Objects, notation, models and imported primitives | Preliminaries and just before a specialized construction. |
| Construction and justification | Algorithms, theorem statements and proofs | Component-by-component or separate construction/security sections. |
| Evidence | Analytical costs, measurements or application validation | Relevant result subsection or a dedicated evaluation. |
| Interpretation | Supported conclusion and meaningful remaining limits | Conclusion if useful; no mandatory word/sentence count. |
| Supporting detail | Full proofs, extra data and reproduction details | Nontrivial full proofs go in the corresponding appendix; body sketches give exact pointers. |

For theory work, reserve body space for the theorem's hypotheses and a concise
proof sketch; place the full proof in the corresponding appendix unless it is
short and straightforward. State the exact appendix destination in the body and
apply the venue's actual inclusion rules. Do not add an experiment to fill a template. For implementation work, explain the changed
algorithm and evaluation scope, and check whether implementation changes affect
inherited security premises. For application/circuit work, introduce the statement,
trust boundary and exact encoded relation early. None of these paper types has an
automatic venue, column count or fixed percentage allocation.

## Page budget and layout

Read the applicable venue/year instructions and user constraints. Record separate
counts and limits for main text, references, appendices and supplementary material
in the project submission notes. If references and appendices are excluded from
the body limit, count them separately. Never infer unlimited appendices or reuse a
different year's rule as current. Mark unresolved rules explicitly.

Allocate the allowed body space by which claims need explanation or evidence.
Revisit that allocation when a proof or experiment needs more space; no section
percentage or last-page target is prescribed. Shorten repeated prose and redundant
tables before adjusting layout. Keep the venue template, font sizes, margins and
spacing requirements; do not use negative spacing or shrinking to hide overflow.
Rebuild and inspect affected pages, floats and references after layout changes.

## Notation and terminology

- Start with the notation of directly relevant prior papers, especially the
  primary baseline, when the objects and definitions match. Follow
  [notation alignment](../references/terminology.md#align-notation-with-prior-work-and-the-baseline).
  Do not invent new symbols for already familiar objects without a concrete reason.
- Maintain `paper/NOTATION.md` or the existing equivalent: symbol, type/domain,
  meaning and first definition. For inherited/changed notation, record the source
  paper and symbol, our symbol and the reason for any deviation. Keep one coherent
  convention and avoid conflicting meanings within the same scope.
- Follow [shared-usage terminology](../references/terminology.md); retain meaningful
  distinctions rather than forcing different definitions into a familiar name.
  Explain uncommon objects before using their labels in the argument.
- The title, abstract, contributions, theorem statements, figures and conclusion
  must describe the same results and premises, though their order can differ.
- Reuse a formula from the formal statement when possible. For an informal
  simplification, state suppressed hypotheses and verify the mapping explicitly;
  literal string identity is neither necessary nor sufficient for equivalence.
- Reference the original theorem label when restating it in an appendix, retaining
  its hypotheses. Avoid global symbol replacement without checking mathematical scope.

## Checklist

- [ ] Section order follows actual dependencies, and missing results were not invented.
- [ ] Main results and material assumptions are assessable in the body; deferred proofs are linked.
- [ ] Applicable body/reference/appendix limits are separately recorded.
- [ ] First-use definitions and established terms are consistent across the manuscript.
- [ ] Layout obeys the template and affected rendered pages are readable.

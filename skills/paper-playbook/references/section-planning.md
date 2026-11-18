# From reference passages to a section plan

Use this method for a new section, a substantial rewrite or a user request for
reference-based structure. Reuse an existing checked plan for small corrections;
do not turn routine polishing into a new literature survey.

## Read the reference for its function

Choose relevant published primary papers first and also inspect user-named works.
Check the actual version and section, not a search snippet or an earlier model's
summary. An extended version can have extra proofs, experiments or different
numbering. See [the source register](source-corpus.md) for the supplied examples.

For each useful passage record in working notes:

`source/version | section/page + paragraph cue | content | function | prerequisites | information supplied next | transferable choice / limit`.

Content answers **what the passage says**; function answers **why the reader needs
it here**. For example, a paragraph introducing a folded instance provides the
output type needed by the next algorithm; a later compression paragraph explains
an additional property and must not be silently merged into the folding guarantee.
These are different jobs even when both paragraphs discuss the same scheme.

- Start at paragraph or argument-unit granularity for long sections. Split a
  paragraph into sentences when it mixes definitions, claims or comparisons whose
  dependency is unclear. Do not require exhaustive sentence tagging of whole papers.
- Record absent functions as absent. Not every paper has a separate contributions
  section, experimental evaluation, conclusion or appendix.
- Separate observed order from your recommendation. Reorder if our reader needs a
  definition earlier, our theorem has extra conditions or the borrowed story does
  not match our result. No requirement to mimic source headings or paragraph counts.
- Paraphrase the structural lesson; borrow established terminology, not distinctive
  sentences. A successful paper's rhetoric is not proof of novelty or correctness.

## Plan the requested section

For a substantial draft, keep a compact `paper/SECTION_PLAN.md` (or the project's
existing equivalent), with a subsection per target section:

`unit | reader question / function | prerequisites | concrete content | claim / evidence / source | resulting dependency | material boundary`.

Each row is a paragraph, definition, algorithm, theorem or figure as appropriate;
it need not become its own heading. Put the task and familiar objects before a
rare name. Put the comparison's scope before its ratio. Put definitions before
algorithms using them and proof premises before conclusions depending on them.
If a plan reveals a missing result, narrow the prose or identify the research gap;
do not make the missing result true by naming it.

Apply [clear exposition](clear-exposition.md): track A → B → C through the actual
objects and operations. Split sentences that introduce different non-obvious
problems; explain the connection before switching to a new obstacle. Mark routine
protocol steps as reused so they do not become contribution bullets or dominate
the abstract. An independent branch needs an explicit transition, not a false
causal link. A substantial reduction needs a mechanism, not just the word “reduce”.

## Reusable function map

| Part | What the reader must learn | Typical dependency to supply |
|---|---|---|
| Introduction | Task, concrete obstacle, result type and scope | Objects and problem the overview addresses |
| Contributions | Distinct established results and their conditions | Pointers to the corresponding theorem or evidence |
| Overview | Central operation and why it helps | An informal model of the construction and its limits |
| Related work | What is shared, changed, complementary or incomparable | Source-grounded positioning and baseline selection |
| Preliminaries | Types, interfaces, notation and existing definitions | Exact objects used by construction and security |
| Construction | Inputs, messages/state, challenges, checks and outputs | Algorithms to which theorem statements apply |
| Security/correctness | Guaranteed property, assumptions and proof steps | Justified interpretation of the construction |
| Evaluation | Questions, configurations, methods, evidence and interpretation | Which practical or cost conclusions are warranted |
| Conclusion | Established answer and remaining boundary | A precise takeaway, not a new result |
| Appendix | Deferred proofs/evidence and their main-text connections | Verifiable support without hidden hypotheses |

These functions can be combined, interleaved or omitted when inapplicable. A
theory paper may have no runtime experiment; a construction may put a theorem
immediately after each component instead of a separate security section. Unless
its proof is short and straightforward, plan a concise body proof sketch and a
complete proof in a specifically labelled appendix subsection. Record the exact
body-to-appendix pointer; keep the theorem and its hypotheses in the body. See
[proof placement](../sections/09_security_correctness.md#proof-placement).

## Draft and review

Proceed to authorized writing after planning. Verify three reading paths:

1. **First-use path:** can a reader identify each symbol/object and the antecedent
   of phrases such as “these coefficients” without guessing or jumping forward?
2. **Argument path:** does each proposed mechanism answer the stated obstacle, and
   does each theorem apply to the actual described algorithm under its premises?
3. **Evidence path:** can every quantitative/comparative conclusion be traced to a
   compatible configuration, source or ledger row, with added costs visible?

Keep detailed source analyses and internal identifiers in working notes. Only
useful definitions, citations, evidence and scope belong in the paper. Review
new editorial choices independently when the project workflow requires it;
this review neither supplies proof verification nor changes a scientific verdict.

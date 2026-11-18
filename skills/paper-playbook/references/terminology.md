# Terminology and source selection

Use familiar terms for familiar objects. Prefer a short ordinary description to a
new label when the description is sufficient. New terminology needs a distinct
concept that recurs and has no adequate established name; define it once and state
the distinction. Internal claim IDs, revision numbers and implementation nicknames
normally stay out of theorem titles and reader-facing prose.

## Choose sources by relevance and status

- Start with the closest published conference/journal papers and inspect their
  actual definitions or algorithms. Use an authoritative textbook for standard
  mathematical vocabulary. Publication is not proof of correctness or applicability.
- Read user-named reference papers even when they are preprints. Check whether a
  published version exists and keep versions distinct. A newer preprint can contain
  details absent from proceedings; attribute those details to that version.
- Do not treat ePrint hosting, acceptance rumors, search snippets or a blog as
  peer review. Attribute a source-specific preprint term as “following X, we call
  ...” when useful; do not present it as field-wide convention. Blogs are secondary
  explanations unless the claim is specifically about that blog or implementation.
- Borrow established technical terms, not distinctive sentences. Cite the source of
  a definition, specialized naming choice or imported construction; common words
  do not need a citation on every occurrence.

## Prefer shared usage over a single paper's vocabulary

- Establish that the candidate terms denote the same object, relation and security
  notion before comparing their use. Among equivalent terms, prefer the one used
  across most directly relevant, independent papers consulted, giving
  priority to published conference/journal papers. One published occurrence does
  not establish a field convention; one prominent or user-named reference does
  not outweigh broader usage merely because it is the closest stylistic model.
- For an unfamiliar or disputed term, inspect definitions in a representative set
  of relevant primary papers, including papers outside the originating work's own
  terminology lineage. Count distinct works using the term for that concept, not
  occurrences of the string, search-result counts, citations or repeated versions
  of one work. Do not count a paper quoting another's nickname as independent adoption.
- If one paper uses term A while the other relevant papers use equivalent term B,
  use B in our own prose, headings and figures. Mention A only when needed to
  identify that paper's construction or compare its notation, and attribute it.
  Apply this rule even when the lone source is published. Reading a user-named
  paper does not require adopting its unusual vocabulary; an explicit user request
  to use that vocabulary remains controlling.
- Retain a source-specific term when it identifies a distinct definition, named
  algorithm or exact API/transcript token, or when discussing that source's usage.
  Explain the distinction rather than forcing it into a familiar but inequivalent
  name. Preserve author terminology in quotations and faithful translations; use
  the common equivalent in our explanations once the correspondence is stated.
- If the inspected literature has no clear preference or is too narrow to judge,
  do not assert a field-wide majority. Use a precise ordinary description or an
  explicitly attributed term, and record uncertainty in the working notes. Lack
  of a clear consensus is not a reason to invent another synonym or acronym.

## Align notation with prior work and the baseline

- For an object with the same definition, prefer the notation already used in
  directly relevant prior papers, especially the primary baseline. Inspect the
  source's actual definitions first; matching letters alone does not establish
  matching objects, domains, dimensions or security parameters.
- For a construction extending or comparing directly with a baseline, use its
  notation as the starting point so readers can compare formulas and algorithms.
  If references use competing conventions, choose one coherent convention, usually
  that baseline's, instead of mixing them. A well-established field convention can
  justify a different choice when it improves clarity; record the correspondence.
- Reuse appropriate field/group symbols, instance and witness notation, size and
  degree parameters, indices, vector/matrix typography and operator notation.
  Do not rename a standard object merely for novelty or cosmetic differentiation.
- Depart only when needed for a genuine definition difference, a symbol collision,
  an incompatible type/domain, or another concrete clarity issue. Make the smallest
  useful change, define it at first use, and explain the relevant correspondence
  in the preliminaries or near the imported definition. Never use the same symbol
  to conceal a different meaning, nor conflate base/scalar fields or different sizes.
- Extend the existing working notation table for reused or changed symbols with
  source paper/section, source symbol, our symbol, meaning/type/domain and the reason
  for any deviation. Do not add a separate manuscript glossary merely for process.
  Preserve source notation in direct quotations and state a mapping when translating
  an imported definition or theorem into our convention.
- Keep the chosen convention consistent across the abstract, body, algorithms,
  tables, figures and appendix. A notation revision must preserve equations,
  quantifiers and assumptions; inspect context rather than blindly replacing text.
  A language-only polish flags notation discrepancies instead of silently changing math.

## Record and check the choice

Before a substantial terminology pass, record a compact working table:
`concept | candidate terms | independent sources and sections | usage in the consulted set | chosen term and reason | definition match or difference`.
Distinguish shared usage, source-specific usage and insufficient evidence. Reuse
already checked papers; investigate genuinely unfamiliar or competing names rather
than running a new literature survey for every standard term. A small checked set
supports a choice for this manuscript, not a statistical claim about the whole field.
Reuse an existing notation table rather than adding a separate glossary to the
paper unless it helps the reader. Source provenance belongs in working notes;
only useful definitions and citations enter the manuscript.

Match the object, relation, quantifiers and security model before reusing a name.
For example, a relation defined by a few matrix evaluations is not automatically
relaxed R1CS; an extra extractor assumption is not a proof of knowledge soundness;
an operation-count reduction is not an end-to-end speedup. If the definitions do
not match, use a plain description and state the difference. The protected pairs
in polish-writing still apply.

## Draft and revise concisely

- Use one name per concept across abstract, theorems, text, figures and supplement.
  Preserve exact code/API/transcript tags when required for reproducibility, but
  explain them in ordinary prose instead of turning each tag into a named concept.
- Do not add acronyms or stacked hyphenated qualifiers to every boundary, step,
  theorem or parameter choice. Name the operation and state its relevant condition
  in the sentence. A method need not receive a brand name.
- Remove repeated motivation, disclaimers and meta-commentary. Put scope in the
  introduction, exact premises in the theorem, and measurement limits beside the
  comparison. Repeat a qualification only where omission would change the claim.
- Review the old-to-new term map against definitions and assumptions after editing.
  Do not shorten away a necessary distinction or fill a gap with a stronger name.
- Check distinctive names in titles, headings, contributions and figure labels:
  being traceable to one reference is insufficient when a semantically equivalent
  term has broader adoption. State the reason for any retained minority term in
  the working notes; preserve necessary source attribution in the prose.

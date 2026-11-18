# 07 Preliminaries

## Reader question and inputs

What objects, interfaces and security notions must I understand before reading the
construction? Read the actual construction and theorem statements first, then
select only background they use. Inputs are the notation list, relation definitions,
THEORY.md assumption ledger and source-checked definitions from LITERATURE.md.

Plan using [section functions and dependencies](../references/section-planning.md).
The [reference analysis](../references/formal-section-patterns.md) contrasts Nova's
commitment/argument/IVC interfaces with Quasar's polynomial/IOR background and
KiloNova's sum-check/PCS/proof-system interfaces. None is a universal subsection list.

## General setting and the Notation subsection

Start Preliminaries with a dedicated `\subsection{Notation}`. This subsection
explains the symbols used in the general setting; its title is **Notation**,
not **Notion** (security notions are separate definitions). Prefer the primary
baseline's conventions when their meanings match, as required by the
[notation-alignment rule](../references/terminology.md#align-notation-with-prior-work-and-the-baseline).

- Introduce groups, fields, operations, identities and generators only as needed.
  For example, when applicable, let $\mathbb G$ be a cyclic group of prime order
  $r$, write its operation additively, and use $\mathbb F_r$ for scalars. For an
  elliptic-curve subgroup over $\mathbb F_p$, distinguish the base field from the
  scalar field and the subgroup from the full curve group. These are illustrative
  conventions, not mandatory letters or assumptions for every construction.
- Define instance/witness notation, vector and matrix conventions, index sets,
  dimensions, degree bounds and the security parameter before their use. State
  each parameter's type/domain and the dependencies needed by later definitions.
  A compact table may supplement the prose; include no unused symbol catalogue.
- Present the general interfaces and symbolic parameters here. Put the actual
  numerical assignments used for evaluation in the experiments/evaluation
  section: selected curve/field and modulus values, bit widths, capacities,
  arities, round/query counts and workload sizes. Do not open the preliminaries
  with an implementation parameter table or repeatedly embed those assignments
  in the background definitions.
- Keep mathematical admissibility conditions beside the definitions or theorems
  that need them: order/characteristic requirements, degree-versus-field bounds,
  capacity inequalities and model or assumption restrictions. Deferring concrete
  values does not defer a premise or remove mathematical constants from formulas.
- Symbolic presentation does not establish a general theorem. Preserve the exact
  supported parameter domain and fixed-instantiation dependencies; replacing a
  constant or a fixed hash by an unconstrained symbol must not enlarge a claim.
  If only a fixed instantiation was verified, say so and point to its explicit
  selection in evaluation. A broader result needs separate scientific validation.
- In evaluation, map each chosen value back to the same symbol and identify
  which configuration was measured, counted or only specified. Check the required
  conditions for that configuration. A theory-only paper need not invent
  experiments: if a concrete illustration is needed, place it in a later, clearly
  labelled instantiation or cost-analysis subsection, separate from Preliminaries.

## Functional outline

| Function | Content | What it enables next |
|---|---|---|
| Establish notation and the general setting | Dedicated Notation subsection; symbolic parameters, groups/fields, domains, sizes and parties, with necessary admissibility conditions | Well-typed definitions and algorithms; concrete evaluation choices are stated later |
| Identify the relation | Public parameters, index or structure if present, public instance and private witness; satisfaction condition | A precise statement of what verification establishes |
| Recall required primitives | Typed algorithms and the exact properties invoked later, with sources | Component calls and composition hypotheses |
| Define claimed notions | Adversary interface, quantifiers, auxiliary input, extractor/simulator access and running time, setup and model | Theorem statements with unambiguous scope |
| Supply reused facts | Lemma, applicable hypotheses, source and brief operational explanation | The exact reduction or cost step that cites the fact |

Order by dependencies. A new relation or primitive may belong at its first use in
the construction rather than among established background. Give a short explanation
before a dense definition when the reader needs its purpose; do not add a fixed
number of introductory sentences or a glossary of unused concepts.

## Definition discipline

- Follow [shared terminology](../references/terminology.md). Use definitions from
  relevant primary sources, prioritising published versions. A source-specific
  name does not establish common usage. Preserve a distinct object rather than
  renaming it to a familiar but inequivalent one.
- Prefer notation from directly relevant prior papers or the primary baseline
  for matching definitions. Check the source's object types, domains and parameter
  meanings before adopting symbols. Avoid unnecessary changes to letters, indices,
  vector/matrix conventions or operators. Follow the
  [notation-alignment rule](../references/terminology.md#align-notation-with-prior-work-and-the-baseline).
- Keep a compact notation table when useful, without a row quota. Define symbols
  before use, including the distinction between the security parameter and a
  numerical security level, base and scalar fields, challenge extensions, and
  total versus individual polynomial degree. Explain necessary departures from
  the baseline near the definition and record the source-to-paper mapping in the
  working notation table; do not make different concepts look identical.
- State every public/private split. For preprocessing, distinguish the index from
  its verifier encoding. For folding or reductions, distinguish input/output
  relations, compatibility conditions and the witness accompanying a reduced claim.
- Define only the security properties actually claimed: soundness is different
  from knowledge soundness; HVZK differs from full ZK. State adaptive choices,
  strict or expected running time, and bounded-depth restrictions where applicable.
- If a PCS is used, list the actual binding, extraction, hiding or homomorphism
  properties needed. Hiding alone does not imply a zero-knowledge protocol.
- If Fiat–Shamir is used, specify the model and the applicable interactive notion;
  put the complete transcript in the construction. An ROM theorem does not by
  itself prove security of a fixed-hash recursive circuit.
- A recalled lemma retains its domain, exceptional events and error/cost parameters.
  Cite the exact version or section. Do not silently strengthen a source definition.

## Checklist

- [ ] Each background item has a downstream use; new contributions are identified.
- [ ] A dedicated Notation subsection defines the general symbols before use.
- [ ] Concrete evaluation assignments appear in evaluation, with an explicit symbol-to-value mapping.
- [ ] Mathematical conditions and fixed-instantiation dependencies remain explicit; symbolic notation has not broadened the result.
- [ ] Every protocol input and theorem parameter has a definition and domain.
- [ ] Notions, quantifiers, model and setup match the theorem and assumption ledger.
- [ ] Imported properties are source-checked, and any adaptation is explicit.
- [ ] Unusual terminology is explained through its mathematical role before use.

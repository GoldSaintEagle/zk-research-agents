# 01 Title

## Reader question and inputs

What result does this paper establish for which object? Read the accepted
contributions, theorem statements, evidence and actual abstract first. A title
must communicate the result to its intended readership without depending on a
later definition of a new name.

## Lead with the established result

Choose the title from the strongest supported result, rather than merely naming
the problem, activity or object under study. Prefer a construction's established
property, improvement, complexity bound or guarantee. An analysis can instead
headline a proved limitation, lower bound or resource trade-off. Result-oriented
wording does not require a positive performance claim.

| Function | Possible content | Dependency/check |
|---|---|---|
| State the result | An efficiency improvement, constant resource, extraction guarantee, bound or trade-off | Identify the exact theorem or evidence that establishes it. |
| Identify the object | Folding scheme, commitment, constraint system or other familiar object | Use a term with the right definition and broad relevant usage. |
| Preserve material scope | Relation class, resource, varying parameter, model or conditional guarantee | Omitting the qualifier must not strengthen the headline. |

Useful forms include **Efficient [object/operation]**, **[object] with Constant
[resource]**, **[object] with [established guarantee]**, and **[proved bound or
trade-off] for [object]**. These are alternatives, not required keywords. The
result need not be the first grammatical phrase, but it should be the title's
main information. A problem-only title such as “Checking [object]” normally needs
the actual contribution; simply adding “Efficient” does not supply evidence.

A system name or subtitle is optional. Nova's published title identifies
recursive arguments and the folding mechanism; HyperNova's title identifies its
relation class. The user-selected Quasar/KiloNova preprint titles have specialized
scopes. These observations from [the actual source titles](../references/source-corpus.md)
are examples, not authority to invent a brand, borrow an unproved property or
adopt a source-specific term.

Apply [the terminology rules](../references/terminology.md). If a rare phrase
needs several sentences of explanation, use a familiar object together with its
supported result. Do not choose a familiar but inequivalent term for brevity.

## Check the headline property

- **Efficient / faster / lower cost:** identify the resource, comparator, parameter
  regime and theoretical or measured basis. When only one cost improves, name
  that cost where needed; fewer primitive operations alone do not establish lower
  total runtime or an efficient complete system. Keep material extra costs visible.
- **Constant:** identify what is constant and with respect to which varying
  parameter. Record dependence on the security parameter, capacities and other
  fixed quantities. A single fixed experimental configuration does not establish
  an asymptotic constant bound. Constant proof size, verifier storage, group
  operations and complete verification time are different claims; a constant
  subroutine cost cannot be promoted to a constant full-verifier cost.
- **Conditional guarantee:** retain a qualifier when omitting it would suggest
  stronger security, generality or a complete instantiation. A theorem under an
  extra knowledge assumption must not become an unconditional security headline.
- Use “unified”, “optimal”, “post-quantum”, “zero-knowledge” or “succinct” only with
  the corresponding scoped result. Do not add a research claim to fit a preferred
  title form, invent an extension for “and beyond”, or hide a missing result in a
  subtitle. If no efficiency/constant-resource result is supported, name the
  established bound, guarantee, construction property or trade-off instead.

## Procedure and checks

- First write one sentence stating the result, its object and material conditions.
  Trace the result to an accepted claim/theorem and any numerical evidence before
  compressing that sentence into a title.
- When alternatives are useful or requested, record a small set in
  `paper/TITLES.md`: candidate, main result, source claim/theorem/evidence,
  necessary qualifier and possible overreading. Prefer the candidate that makes
  the contribution clearest at its actual scope; no fixed count is required.
- Check title, abstract and contributions against the same accepted claims.
  Result-oriented wording does not change the scientific scope.
- A request for candidates does not itself select or apply one to the manuscript.
  If title revision is already authorized, do not add an unnecessary approval round.
- When a title is applied, inspect the actual rendering and matching submission
  text. Rephrase an awkward wrap without shrinking the template's title font.
  No universal line/word quota applies.

Synthetic example: if a hypothetical theorem establishes verifier storage
independent of batch size, “Batched Polynomial Evaluation with Constant Verifier
Storage” communicates that result. It does not claim constant verification time
or a complete SNARK. The example supplies a title pattern, not a scientific result.

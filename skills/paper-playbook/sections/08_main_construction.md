# 08 Main construction

## Reader question and inputs

What is computed or proved, how do the algorithms do it, and why do their outputs
meet the next component's requirements? Use survived/weakened CLAIMS rows, the
actual definitions and proofs in THEORY.md, and the specification or implementation
being described. Identify theoretical parameters separately from implemented ones.

Use [section planning](../references/section-planning.md) and the
[source examples](../references/formal-section-patterns.md). Nova motivates a
relation change by failed direct folding; HyperNova explains a small case before a
general protocol; Quasar separates an oracle reduction from commitment compilation.
Use whichever route clarifies the actual construction.

## Functional outline

| Function | Concrete content | Dependency supplied |
|---|---|---|
| State the task | Input/output relation or invariant, intended caller and exact scope | Why this component is needed |
| Explain the operative idea | A useful small case, obstruction or identity, if it clarifies the design | Why the algorithm's steps are present |
| Define the interface | Setup/indexing, public and private inputs, state, outputs and failure cases | Executable specification |
| Specify the algorithm | Ordered messages or computations, domains, randomness, checks and updates | Objects referenced by the proof |
| State the guarantee | Completeness/correctness and the security properties actually established, under all premises | What a caller may rely on |
| Compose or instantiate | Actual component interfaces and imported theorem hypotheses, if applicable | End-to-end guarantee for the stated setting |
| Account for costs and limits | Separate operations, storage, setup, communication and omitted work | Honest interpretation of the gain |

These functions may share paragraphs or span multiple sections. A theorem can
precede or follow its algorithm when its objects are already defined. No mandatory
PIOP, PCS, Fiat–Shamir, final SNARK, parameter search or worked example is implied.

## Specification and proof interface

Follow [clear exposition](../references/clear-exposition.md). Explain the operation
and intermediate representation before specifying the next check. When appropriate,
present the interactive protocol first, then state the justified Fiat–Shamir
transformation briefly with its model/security reference. Keep the detailed
transcript in one reconstructible specification or referenced appendix. This
reduces rhetorical emphasis on standard steps, not their technical requirements.

- Algorithms use typed inputs/outputs and stable step labels. Show message order,
  exact challenge distribution, every acceptance check, exceptional case and output.
  An interactive two-column box, pseudocode or a mathematical definition is chosen
  for clarity; a box layout is not a security property.
- Keep oracle access distinct from commitments and openings. For an oracle model,
  give oracle types and degree bounds. For a compiled protocol, show what is sent
  and verified. State all compiler preconditions and changed guarantees, using
  [piop-pcs-compile](../../piop-pcs-compile/SKILL.md) when that route applies.
- Specify Fiat–Shamir absorption order, index/statement binding, parameters, domain
  separation and serialization through the actual transcript definition. Refer to
  [fiat-shamir-audit](../../fiat-shamir-audit/SKILL.md); do not replace the transcript
  by an incomplete generic hash expression or assume ROM security survives fixed
  hash instantiation without an applicable argument or explicit assumption.
- Explain recursive state and base cases, what an accumulator attests to, what the
  next step checks, and what the final verifier or decider still must do. A reduced
  claim is not a completed proof of that claim.
- All theorem hypotheses, field/domain conditions and exceptional events are
  explicit. Check each claimed parameter set against them. State sufficient
  conditions as sufficient; do not present them as necessary or optimal.
- Unless a proof is short and straightforward, give only a concise, labelled proof
  sketch beside the body result and place the complete proof in the corresponding
  appendix. Explicitly point to that appendix subsection, retaining the full theorem
  statement and hypotheses in the body. Follow the
  [proof-placement rule](09_security_correctness.md#proof-placement).
- A design choice may follow algebra, an engineering constraint or a search.
  Report a search only if it was run; report optimality only over its proven or
  measured scope. Do not invent a parameterised family to make a result sound broad.

## Cost and terminology discipline

Use the same definitions of cost throughout the paper, but retain separate units
for field arithmetic, group operations, hashes, bytes and memory. Combining them
requires a justified cost model. Include public-input processing, setup and final
verification where relevant; label excluded work. Counts, constructive upper bounds,
estimates and measurements are different results and each own numerical result
needs EVIDENCE provenance.

Use [shared vocabulary](../references/terminology.md), explaining uncommon objects
through their operations before naming them. Mark imported, adapted and new
components without giving every ordinary step a new name. A worked example is
optional; when included, compute its values and record the evidence.

## Checklist

- [ ] Inputs, outputs, relation, checks and message order are reconstructible.
- [ ] Theorem objects are defined, assumptions visible, and parameter cases covered.
- [ ] Every actual composition has its required interface and security properties.
- [ ] Costs retain their units, scope and provenance; no local saving implies an
      unmeasured total improvement.
- [ ] The overview and implementation describe the same construction or explicitly
      distinguish the implemented subset.

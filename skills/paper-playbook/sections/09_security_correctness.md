# 09 Correctness and security

## Reader question and inputs

Exactly which guarantee follows for the specified algorithms, against which
adversaries, in which model, and under which assumptions? Read THEORY.md and its
assumption ledger, the actual proof and algorithm, CLAIMS verdicts, and any
applicable [zk-definitions](../../zk-definitions/SKILL.md) or
[soundness-budget](../../soundness-budget/SKILL.md) records.

Plan by [functions and dependencies](../references/section-planning.md); consult
the [formal-section examples](../references/formal-section-patterns.md). Security
may be proved beside each construction or in a separate section. Completeness,
knowledge soundness, zero knowledge and concrete security are distinct obligations;
include those claimed, rather than forcing four theorems every paper does not have.

## Functional outline

| Function | What the prose/formula must establish | Dependency |
|---|---|---|
| Fix the experiment | Parties, adaptive choices, public/auxiliary input, oracle access, setup and success event | Defines the claim's meaning |
| State the theorem | Exact quantifiers, notion, hypotheses, error and resource bound as established | Delimits what is being proved |
| Explain the argument | Key invariant, reduction or extraction/simulation strategy in words | Makes proof obligations visible |
| Discharge obligations | Lemmas tied to algorithm checks; each imported result's hypotheses checked | Connects the stated algorithm to the guarantee |
| Compose bounds | All bad events, reductions, runtime and repetition losses for the actual composition | Justifies the final bound |
| Interpret the scope | Conditional, asymptotic or numerical status, and remaining restrictions | Prevents stronger downstream claims |

## Proof placement

Unless the proof is short and straightforward, place the complete formal proof in
the corresponding appendix. In the body, keep the full theorem statement and its
material assumptions, then a concise paragraph labelled **Proof sketch** explaining
the key invariant, reduction or lemma dependencies. End with an explicit pointer,
for example: `The complete proof appears in Appendix~\ref{app:proof-main}.`
Use a dedicated appendix subsection label when an appendix contains several proofs.

A short direct derivation from already stated definitions or lemmas can remain in
the body as a complete proof. A proof needing substantial case analysis, multiple
hybrids, a recursive extraction argument or a long technical derivation normally
belongs in the appendix. Judge simplicity by the actual argument, not by calling
a difficult step “standard” or omitting it; there is no universal line-count cutoff.

The sketch should explain why the theorem follows without repeating the complete
derivation. Retain the statement's quantifiers, conditions and guaranteed bounds
in the body; do not hide a hypothesis in the appendix. Keep the complete proof
available and consistent with that exact statement. Record each nontrivial result's
proof destination in the existing section plan, and check the cross-reference in
the compiled manuscript. A sketch is not a substitute for completing the proof.

Apply actual venue requirements if they explicitly constrain this placement, and
record any necessary exception. Here “formal proof” means the complete mathematical
argument; it does not by itself imply machine-checked formalisation.

## Proof obligations, when applicable

**Correctness/completeness.** Walk through the verifier checks or transition
invariant for honest inputs. Treat aborts, division by zero, empty/padded cases and
recursive base cases explicitly; name any nonzero completeness error. Small-field
checks and formalisation support, but do not replace, the stated general proof.

**Soundness/extraction.** Define the adversary, extractor access (including
rewinding or oracle programming), output relation, success probability and total
running time. For recursion include depth, branching, repeated predecessors and
all replay costs where they enter the proof. Do not infer knowledge soundness from
ordinary soundness. State whether outputs or distributions are preserved if the
composition relies on that property. Use the extraction procedure actually proved;
binding commitments alone do not give an extractor, and collecting transcripts
requires a justified probability and runtime argument.

**Zero knowledge.** State honest-verifier or full ZK, perfect/statistical/
computational indistinguishability and simulator resources. Describe how the
simulator reproduces the complete claimed view, including revealed evaluations,
commitment openings and public sizes. Account for oracle programming and hiding
hybrids when used. Commitments being hiding is insufficient by itself. A non-ZK
intermediate state and a ZK final proof are different objects.

**Composition.** Check relation and interface compatibility, adversary model,
setup, extractability and runtime conditions of every theorem invoked. Separate
interactive security, ROM compilation and concrete-hash assumptions. State new
knowledge assumptions and conjectures in the theorem premises; a published
example of such an assumption is not a proof of it. System or circuit changes
require their own argument that the imported theorem still applies.

## Error bounds and numerical security

- Give the bound the proof actually establishes. Keep an asymptotic negligible
  claim asymptotic unless a concrete reduction is available; an unquantified
  assumption cannot be turned into a numerical security level by choosing a field.
- Itemise applicable bad events and reduction losses. A PIOP/PCS/Fiat–Shamir split
  is useful for that compiler, not a universal formula. Do not assume losses add
  or equal query count times interactive error without the relevant theorem.
- When numerical security is claimed, use the soundness-budget record with
  parameters, attack/query budget, level definition, source and status of each
  term. Sum probabilities as justified, not just the minimum of per-term bits.
  Distinguish proven bounds, conjectures and heuristic estimates. Separate totals
  are needed when reporting different regimes, not empty conjecture columns when
  no conjecture is used.
- If a term is unknown or an assumption unquantified, show that gap and limit the
  conclusion. Comparisons labelled equal-security require compatible guarantees;
  descriptive component costs may be reported without that label.
- Record all own printed numerical bounds in EVIDENCE. Keep limitations beside the
  affected theorem; explain their consequence and supported applicability using
  [limitations and applicability](../references/limitations-and-applicability.md).
  A depth/arity or representation workaround must preserve relation semantics and
  account for its changed extraction resources and failure bound; motivation does
  not discharge those obligations.

## Checklist

- [ ] Every claimed property has a matching definition, theorem and actual proof.
- [ ] Quantifiers, model, setup, assumptions and extractor/simulator resources match.
- [ ] All composition premises and relevant errors/runtime losses are accounted for.
- [ ] Numerical, asymptotic and conditional guarantees remain distinguishable.
- [ ] Nontrivial full proofs are in their corresponding appendices; body sketches
      are concise, labelled, and explicitly reference the exact proof destinations.
- [ ] Any full proof retained in the body is short and straightforward, or its
      required venue-specific exception is recorded.
- [ ] Computational checks do not become universal proofs; all deferred proofs exist.

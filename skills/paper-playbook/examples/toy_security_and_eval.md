# Toy formal exposition and evaluation examples

These are synthetic writing exercises, not established cryptographic protocols,
proofs or benchmark records. They illustrate functional organisation. Any symbols
for errors or times stand for values a real project must justify; do not copy them
as a generic security theorem.

## A theorem before and after scope repair

Bad: “The construction is secure and zero knowledge.”

Better structure: identify the particular protocol, relation and security experiment;
state the model, assumptions and adversary/extractor resources; then state the
property proved and its exact error bound. If only a conditional extraction theorem
has been established, name its knowledge assumption in the statement. Do not add a
simulator or a numerical security level to complete a template.

| Unit | Content in a hypothetical extraction result | Why it belongs here |
|---|---|---|
| Statement | Under assumption A, the named extractor produces a witness for relation R with the proved failure bound B and total runtime bound T | Makes the guarantee and conditions explicit |
| Strategy | Explain which transcript information recovers the witness | Gives the reader a route through the proof |
| Lemmas | Establish extraction, consistency and all applicable bad-event/runtime bounds | Connects the strategy to actual obligations |
| Conclusion | Combine the lemmas under their common premises | Supports B and T, without inventing their form |

Bad inference: “The PCS is hiding, so the protocol is statistically zero knowledge.”
Repair: determine what transcript values are revealed, supply the actual simulator
and distribution argument, or remove the unsupported ZK claim. Likewise, an
interactive error multiplied by a query count is not automatically a valid
Fiat–Shamir theorem.

## A component evaluation without a system claim

Synthetic setting: an implementation replaces one commitment subroutine; recorded
experiments cover only that subroutine. The full recursive prover is unimplemented.

| Function | Appropriate prose content | Unsupported extension |
|---|---|---|
| Scope | Identify the subroutine inputs and the timed operations | Call the result end-to-end proving time |
| Conditions | State baseline, inputs, machine, included work and security status | Assert equal security from equal parameter labels |
| Result | Report the recorded time and uncertainty with its evidence row | Fill missing proof-size or full-system cells |
| Interpretation | Compare the measured subroutine under those conditions | Infer full-system speedup from one component |
| Limit | State unmeasured integration, memory or setup costs that matter | Hide them in a distant appendix |

Use ratios only for matched measurements. A reported value from another paper
with different hardware can provide context, with the difference stated, but does
not acquire comparability by being placed in the same table. An ablation that
finds no benefit still answers a question; it should not be rewritten to claim
that all components are necessary.

## Circuit correctness is a relation claim

Bad: “All witnesses were unique on a small field, so the circuit is correct.”

Better structure: specify the intended relation and allowed witness multiplicity;
check under- and over-constraint, witness generation, ranges and field wraparound;
report exactly which exhaustive or differential tests ran, then state their limited
scope. Uniqueness is a requirement only when the specification needs it. Small-field
tests do not prove all-field correctness, and range bounds must justify each
arithmetic operation rather than assume products never wrap.

## Deferred proof

The body states the theorem with all assumptions and describes the key reduction.
The appendix identifies that theorem, recalls the setup, proves the deferred lemmas
and reconnects them to the result. A precise body pointer reaches the full proof.
The appendix contains detail, not a previously undisclosed hypothesis.

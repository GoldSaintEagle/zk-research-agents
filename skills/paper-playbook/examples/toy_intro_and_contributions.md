# Synthetic introduction and contribution examples

These examples illustrate writing decisions, not established lookup constructions,
empirical results or literature claims. Placeholder references A and B are
fictional. In an actual paper, accepted claims and source-checked evidence must
replace the hypothetical inputs before prose enters the manuscript.

## Hypothetical inputs

Suppose a paper proves an operation-count bound for a specified class of lookup
tables and implements only its commitment-construction component. It has no
complete-system timing result and no new zero-knowledge theorem. Its theorem
requires a table representation with a stated evaluation property.

## Introduction: diagnose the missing information

Bad:

> We introduce a universal folding-aware lookup accelerator that resolves the
> inefficiency of existing proof systems. Our framework opens a new dimension.

The reader does not know what is computed, what “universal” means, which cost is
reduced or which assumption is needed. New labels hide these missing facts.

Better, conditional on the hypothetical inputs above:

> A lookup argument checks that witness values belong to a specified table. In
> the construction considered here, committing to the table-dependent vectors
> contributes to prover work. We study tables whose representation permits the
> evaluations required by our construction to be computed succinctly. For that
> class, we give a different representation of the committed data and bound its
> commitment work. We also measure the commitment-construction component; these
> measurements do not establish a speedup for a complete lookup argument.

Function map: task → particular cost → required table property → deliverable →
evidence boundary. A real draft supplies the exact property and the theorem/cost
references. No global open problem, numbered objective or new acronym is needed.

## Contributions: match the available results

Bad:

> We prove Theorem 3, unify prior approaches, implement everything, and obtain
> practical zero-knowledge proofs.

This hides the actual result and promises unsupported scope. The theorem pointer
itself is not the problem; the missing description and unsupported properties are.

Better, still hypothetical:

- **Representation and operation count.** We give a representation for tables
  satisfying the stated evaluation property and prove the commitment-work bound
  in the main theorem. The bound includes the representation's preprocessing cost.
- **Component evaluation.** We implement the commitment-construction stage and
  compare it with the direct construction under matched inputs. The evaluation
  reports both its runtime and storage requirements; it does not cover the rest
  of the argument.

Two contributions suffice for these inputs. A theorem pointer, a necessary
qualification and the cost of the gain can all appear in a contribution. Do not
add security, compiler or experiment bullets merely to fit a preferred count.

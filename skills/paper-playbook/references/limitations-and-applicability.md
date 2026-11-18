# Explain limitations and justify applicability

Use this guidance when a material restriction could change how the reader judges
the contribution: bounded depth, finite capacity, restricted relations, extra
assumptions, setup, component-only evaluation or a limited parameter regime.
Do more than list the restriction. Explain what useful result survives, for whom,
and why the supported setting matters. The goal is an evidence-based case for the
contribution, not a guarantee of significance or a rhetorical defence of any limit.

## Build a justification beside the affected result

For each material limitation, extend the existing section plan with:

`restriction and quantifiers | affected guarantee | applicable workload/class | why the restriction is acceptable there | mitigation or transformation | correctness conditions | additional costs and assumptions | theorem/evidence/source | residual gap`.

1. State the restriction precisely. Distinguish an upper bound from an exact size,
   a selectable public bound from a universal constant, and a theoretical limit
   from an implementation choice. Do not silently reverse quantifiers.
2. Explain its effect on the result. Identify what remains established and what
   is excluded, using the actual relation, theorem and evaluation scope.
3. Give a concrete justification where supported: a bounded application budget,
   a workload family within the admitted domain, a proved reduction to that domain,
   or a measured regime where the restriction is compatible with the intended use.
   Explain how that workload maps to the construction. An application name alone
   does not establish compatibility or practical relevance.
4. If proposing a workaround, specify its input/output relation and why it
   preserves the statement and witness semantics. Charge increased circuit size,
   arity, prover work, storage, communication, setup and extraction/security loss
   as applicable. A change of parameters or representation may need a new proof
   or experiment; prose cannot supply that validation.
5. Distinguish **established applicability**, a **conditional extension**, and an
   **unresolved limitation**. Cite checked primary literature for imported methods
   and prefer published papers for research claims. Official system documentation
   can support a named implementation example, not a theorem about our system.
6. Conclude with the contribution that is still supported. If evidence is missing,
   retain the gap and identify the needed check; do not assert “practical”,
   “without loss of generality”, or “arbitrary computations” to protect the story.

## Placement

- Introduction/contributions: state the material restriction together with a short
  reason the supported setting remains useful. Do not bury either in an appendix.
- Construction/overview: describe a proposed representation change or workaround
  with its interface and assumptions; separate the existing construction from an
  unimplemented extension.
- Security: retain the exact theorem domain and show what the workaround would
  change in assumptions, extraction resources and failure bounds.
- Evaluation: substantiate claimed practical acceptability and account for the
  workaround's costs. A theoretical possibility is not a performance measurement.
- Conclusion: give the established implication and residual limit without
  repeating a generic disclaimer in every paragraph. No mandatory new subsection
  or fixed number of examples is needed.

## Synthetic example: bounded recursion depth and wider aggregation

This example explains a conditional argument pattern; it is not an application
claim for any manuscript.

**Clarify the graph and the bound.** A recursive ancestry height bounded by $d$
need not be an exact execution length, the number of machine instructions, or a
constant independent of input size. Distinguish execution dependencies, proof
aggregation dependencies and the extraction tree obtained by unfolding repeated
predecessors. The number of inputs folded at one node is its arity; it is not the
same quantity as the maximum number of nodes on a level (tree width).

**When increased arity can help.** Suppose $n$ segment claims can be correctly
merged in a balanced tree with at most $q\geq2$ children per node, leaves at
height zero, and a supported merge relation. Then the ideal aggregation height is
$\lceil\log_q n\rceil$. For a fixed positive height budget $d$, such a tree has at
most $q^d$ leaves. Covering larger $n$ at that same budget therefore requires a
larger arity or more computation per leaf. This tree-counting observation is not
a proof that a particular protocol implements the required merge.

**Separate execution from verification.** Increasing parallel capacity alone does
not remove the dependency chain of an unchanged computation DAG. However, after
a sequential execution trace is available, independently proved segments can
sometimes be aggregated in a shallower proof tree. A toy segment relation could
certify $F^\ell(s)=t$; composing two adjacent segments requires matching the first
output to the next input and binding the program, order and claimed length.
An actual machine relation must additionally enforce all relevant boundary,
memory/state and public-input consistency. Folding several valid instances does
not automatically establish these connections. Do not confuse lower proof-tree
height with parallel generation of the sequential trace.

**Account for the price and quantifiers.** With fixed arity $q$ and height $d$, the
tree has at most $\sum_{i=0}^{d}q^i$ node occurrences; fixed per-node capacity also
bounds represented work. “For each finite input, some larger parameters suffice”
is different from “one fixed configuration handles arbitrarily large inputs”.
Grouping more steps in each node can reduce recursive height, but moves work
into its relation/circuit. Raising arity can increase input processing, key and
circuit sizes, witness storage and extraction/error terms. Recompute these under
the new configuration rather than treating width as a free resource.

**Write only the justified conclusion.** A supported batch budget or a verified
segment-composition construction can justify a bounded-height regime. Without
that mapping, present it as a possible extension with explicit obligations, not
as a demonstrated reason the restriction is harmless for arbitrary computation.

### Public background for the example

- [Umut A. Acar, Parallel Computing: Theory and Practice, sections 1.1–1.3](https://www.cs.cmu.edu/afs/cs/academic/class/15210-f17/www/concurrency.html)
  defines execution DAG dependencies and span. It supports the execution-path
  distinction, not a lower bound on proof aggregation depth.
- [RISC Zero, Proof System Overview, Types of Receipts](https://dev.risczero.com/proof-system/)
  describes segment receipts and their aggregation via a recursion circuit.
  This is an attributed implementation example, not peer-reviewed support for
  an arbitrary-arity compiler or for another construction's extraction theorem.

## Final check

Can the reader identify the restriction, a concrete useful setting, the source of
the applicability argument, its extra cost, and what remains unproved? If not,
repair the missing explanation or retain the limitation; do not upgrade the claim.

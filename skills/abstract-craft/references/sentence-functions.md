# Sentence functions: two folding-paper abstracts

These public abstracts illustrate information order. They do not prescribe seven
sentences, a three-paragraph format, a named scheme, or a particular strength of
claim. Analyse the actual version requested by the user; titles and abstracts change.

Sources inspected: [Quasar](https://eprint.iacr.org/2025/1912), revision listed
2026-03-18, *Sublinear Multi-Cast Commitment Mixing in Recursive Accumulation*;
[KiloNova](https://eprint.iacr.org/2023/1579), revision listed 2026-02-17,
*Preprocessing Folding-based SNARKs for Machine Executions*. Both official records
were marked Preprint. The following tables paraphrase their seven abstract sentences
in order. Rhetorical roles are our analysis, not verified security/performance results.

## Quasar: begin with the operation that costs too much

| Sentence | Content in brief | Rhetorical function |
|---|---|---|
| Q1 | Combining committed objects has a per-step cost linear in instance count. | Identify setting, operation and measurable bottleneck. |
| Q2 | Define the instance-count parameter and the commitment-combination cost unit. | Give the reader the vocabulary needed for the comparison. |
| Q3 | Announce the reduced combination cost while retaining linear public-input processing. | Connect challenge, contribution and boundary in one claim. |
| Q4 | Commit to a union polynomial and check a random partial evaluation. | Explain the reduction through actions and its output. |
| Q5 | Compose with ordinary folding and state separate field/commitment costs. | Move from mechanism to the accumulated construction. |
| Q6 | State prover and other properties under suitable commitment instantiations. | Explain instantiation-dependent consequences. |
| Q7 | Connect accumulation to multi-instance IVC. | Return to the application-level purpose. |

Transferable pattern: **operation and bottleneck -> definitions -> bounded headline
result -> mechanism -> composition -> conditional properties -> application**.
The local cost reduction is qualified immediately, not repaired by a distant
disclaimer. The mechanism is explained even though it also receives a name.

## KiloNova: narrow the application problem before naming the method

| Sentence | Content in brief | Rhetorical function |
|---|---|---|
| K1 | Computation verification faces circuit-growth problems in applications. | Supply familiar context and a concrete scaling motivation. |
| K2 | Existing folding recursion struggles with non-uniform circuits. | Narrow the broad motivation to the targeted limitation. |
| K3 | Introduce a preprocessing recursive SNARK for machine execution. | Identify the contribution's type and target. |
| K4 | Describe folding relations with differing indices. | Introduce the core technical capability through its objects. |
| K5 | Build multi-predicate PCD with constant-size intermediate instances. | Connect the primitive to system organisation and costs. |
| K6 | Compile through polynomial commitments to the target SNARK. | Complete the chain from component to final system. |
| K7 | Invoke analysis and experiments for performance/application claims. | Name the evidence category and intended significance. |

Transferable pattern: **application -> precise limitation -> contribution class ->
core technique -> intermediate system -> final compilation -> evidence/significance**.
Do not inherit the source's broad performance adjectives. Its last sentence gives
no numerical comparison scope inside the abstract. A paper without a final SNARK
or experiments must omit those moves rather than imply it has those results.

## Build an outline for a different paper

1. Choose the entry point the intended reader can understand: the application or
   the concrete operation. Identify the objects and the relevant scale.
2. State the precise difficulty and any definition needed to understand it.
   Do not claim a field-wide open problem when the result addresses a local issue.
3. State what kind of result the paper contributes and its scope.
4. Explain the operative idea as actions on already introduced objects. A coined
   noun cannot replace its input, purpose and output.
5. Follow actual dependencies to the guarantee or composition result, retaining
   premises. Explain a conditional theorem as conditional.
6. Give supported evidence with scope, comparison target and material trade-offs.
7. End with the conclusion the evidence permits. An artifact sentence is optional;
   a material limitation belongs next to the result it qualifies.

Use the sentence-function table in SKILL.md to map these moves onto the actual
contribution. Combine adjacent roles or split a dense sentence. Do not require
every abstract to have every role, a fixed paragraph count, named prior routes with
venue/year, or a separate “However, ... remains open” sentence.

## Reader dependency check

For each sentence ask: which objects does the previous text make available, which
new term appears, what does the sentence add, and what later sentence needs it?
If an unusual name appears before the reader knows its purpose, replace it with a
short concrete description or explain the role at first use. If the sentence only
repeats importance, novelty or a disclaimer, combine it with the relevant result or
remove it. Preserve limitations that change the theorem or comparison, not ritual prose.

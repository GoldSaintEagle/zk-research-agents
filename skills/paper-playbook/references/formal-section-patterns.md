# Formal and evaluation sections: observed functions

Use this reference when planning preliminaries, construction, security, evaluation,
conclusion or appendices. It applies the abstract's content/function/dependency
method to paragraphs and argument units. Sources and version distinctions are in
[source corpus](source-corpus.md); the reusable planning procedure is
[section planning](section-planning.md). Page numbers below are PDF page numbers
of the inspected copies, not interchangeable proceedings pagination.

These are concise structural observations from actual passages, not validations
of their theorems or measurements. A useful explanatory move can be adopted without
adopting its technical claim, name, implementation or section arrangement.

## Preliminaries: explain the interfaces the reader will use

| Source and locator | Unit content | Function and next dependency |
|---|---|---|
| Nova, published §2, PDF pp8–10 (proceedings pp366–368) | Setting paragraph fixes the field and asymptotic convention; §2.1 states needed commitment properties before its algorithms; §2.2 defines arguments; §2.3 explains IVC before formal syntax | Move from basic types to primitive interfaces to the recursive task. The definitions supply inputs and properties later constructions invoke. |
| HyperNova, extended §2, PDF pp14–15 | Recalls relaxed R1CS for specified later uses; defines committed relations generically; then instantiates that definition for CCS and relaxed R1CS | Explain why background is present, factor shared syntax, then distinguish concrete relations. Similar names do not justify identifying different relations. |
| KiloNova, public §3.2–3.4, PDF pp12–14 | Sum-check description ends with the residual evaluation claim; PCS syntax follows; proof-system definitions specify the knowledge experiment | The output of one primitive motivates the next interface. Syntax and security properties have different roles. |
| Quasar, public §3.2–3.3, PDF pp13–14 | Polynomial notation precedes sum-check; the IOR paragraph explains that the verifier may output a claim without reading the oracle fully | Define what a reduced claim means before the construction relies on deferred verification. |

Derived outline: setting → required objects/interfaces → actual security notions
and reused facts, ordered by first use. New primitives can instead be defined in
their construction section. A universal PIOP/PCS/FS background checklist would
obscure papers using a different route.

## Construction: make the algorithm's steps necessary to the reader

| Source and locator | Successive paragraph or argument units | Function and dependency |
|---|---|---|
| Nova §4.1, PDF pp13–14 | Select and define R1CS; attempt a direct linear combination; expose algebraic obstructions; introduce extra terms; verify the new identity; explain the remaining communication/privacy problem and add commitments | A concrete failed attempt motivates each added object. The relation change is explained before readers encounter the final protocol. This is an available route, not a requirement to invent a failure story. |
| HyperNova extended §4, PDF p17, then protocol/proof on p21 | Specify the two relation classes and compatibility; explain the small case; reduce their claims with sum-check; combine compatible outputs; give the general protocol and proof intuition | A small instance explains the general algorithm while preserving the input/output relation. |
| Quasar §4.1, PDF pp15–16 | Declare oracle-model scope and deferred PCS compilation; define the source relation; state the reduction goal; give ordered interaction and output phases; explain union oracles and partial evaluations | Model and output contract precede message details. The reader can distinguish an output obligation from a verified final statement. |
| KiloNova §4.2, PDF pp17–18 | Explain challenge compatibility; introduce a two-input case; specify relation tuples and setup/indexing; present prover/verifier computations | Algorithm parameters and relation types make the subsequent folding equations interpretable. |

Derived outline: task and relation → useful mechanism explanation → typed
algorithm → guarantee → actual composition → costs. Do not impose this order when
a different ordering removes forward references; preserve the same reader needs.

## Security: expose what the theorem assumes and proves

| Source and locator | Observed units | Function and dependency |
|---|---|---|
| Nova §4.1–4.2, PDF p16 | Proof intuition describes witness recovery and binding; noninteractive construction follows; an explicit RO-instantiation assumption accompanies the concrete-hash step | Separate a proof route from a further assumption. Published placement does not establish that assumption for another protocol. |
| Nova §5.1–5.2, PDF p20 | Knowledge-soundness sketch gives the recursive extraction invariant; efficiency is a separate lemma; compression discussion explains missing properties of the intermediate proof | Security, cost and final-proof properties are different obligations. |
| HyperNova extended §4 PDF p21 and Appendix H.1 p70 | Main text supplies extraction intuition and points to deferred proof; the appendix restates the relevant setup and begins completeness with the input relations | The body provides the argument map; the appendix discharges its detailed obligations. |
| KiloNova §5, PDF p25 | The theorem explicitly restricts depth and names the model; proof is deferred; separate complexity discussion distinguishes native and recursive work | Keep scope in the statement and performance outside the security inference. |

Derived outline: experiment and theorem → proof strategy → supporting lemmas →
composition of the actual bounds → scope. It does not require zero knowledge,
negligible error or concrete bits if those properties have not been established.

## Evaluation: define the measured object before interpreting results

| Source and locator | Successive paragraph functions | Dependency created |
|---|---|---|
| Nova §1.3, PDF p5 | Identify implementation/backend; define recursion overhead and show its breakdown; give machine/workload/metrics; distinguish IVC and compression results | A cost label is tied to a particular operation and implementation stage before comparison. |
| KiloNova §7.1–7.2, PDF pp28–30 | Theoretical comparison fixes a common case and discusses trade-offs; prototype paragraph states its implemented relation subset; platform and experimental parameters follow; table discussion identifies excluded or restricted comparators | Theory and implementation have separate scopes; table restrictions matter to the interpretation. Do not inherit its performance adjectives or extrapolations as evidence. |
| Quasar Appendix C, PDF p38, paragraphs 1–4 | First identifies component metrics and explicitly excludes full IVC; then describes platform; then backends; then missing components and circuit instrumentation | Scope precedes results. An incomplete integration can still support a clearly delimited component study. |
| Quasar Appendix C.1, PDF p39 | Parameters and workload precede results grouped by backend; additional table varies arity and degree | Distinguish varied factors from held-fixed factors before reading trends. |

Derived outline: question/scope → conditions and method → observation → supported
explanation → trade-off. A paragraph's persuasive effect is not proof of causal
attribution; our own experiment still needs appropriate controls and provenance.

## Conclusion and appendices: close the result and locate its details

Quasar §7 (PDF pp28–29) recalls the recursion bottleneck, summarizes its mechanism
and cost distinction, then states integration limits and future directions. The
sequence closes the motivation-to-result loop. It is longer than a fixed
two-sentence conclusion. The inspected Nova proceedings paper has no standalone
conclusion or appendix: §6 ends before References on PDF p28, and body passages
point to the full version. Do not invent either section to claim a common pattern.

HyperNova's extended Appendix H.1 (PDF p70) begins by naming the body theorem,
then states the lemma, setup, satisfying inputs and derivation. KiloNova Appendix
B starts formal definitions (p36), C starts folding proofs (p41), and D provides
PCD details. These units serve different checking tasks. Their placement illustrates
how to link a body claim to detailed support; it does not justify hiding material
assumptions or ignoring a venue's appendix rules.

Derived conclusion outline: established result → significance → material boundary
→ optional next question. Derived appendix-unit outline: body obligation → needed
setup → detailed support → connection back. The writing policy for new drafts is
to put nontrivial complete proofs in the corresponding appendix, leaving a concise
labelled proof sketch and exact appendix pointer in the body. Short, straightforward
proofs may stay in the body. This policy is an editorial preference, not a claim
that every reference uses that placement. See
[proof placement](../sections/09_security_correctness.md#proof-placement).

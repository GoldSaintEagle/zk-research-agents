# 12 Appendix and supplementary material

## Reader question and inputs

Where can I check the details supporting a stated result? Use the body statements,
proof inventory, experiment/artifact records and the actual venue's rules on
appendices, supplementary files and page counting. Do not assume appendices are
unlimited, excluded from a limit, or guaranteed to be read.

See [section planning](../references/section-planning.md) and
[reference placement examples](../references/formal-section-patterns.md).
HyperNova's extended version groups deferred proofs; KiloNova separates formal
definitions, folding details and PCD details; the inspected Nova proceedings
version points to its full version. These are alternatives, not a fixed appendix list.

## Functional outline for each appendix unit

| Function | Content | Dependency |
|---|---|---|
| Locate the obligation | Exact body theorem, definition, algorithm or comparison supported | Why the reader follows this pointer |
| Recall the setup | Applicable notation, assumptions and inputs, by reference where possible | Self-contained reading of the detail |
| Supply the detail | Full derivation, algorithm, dataset/table, parameter computation or reproduction recipe | Evidence needed to check the obligation |
| Close the link | State what has been established for the referenced result | Connection back to the body |

Choose grouping by mathematical dependency or by the body results. Not every
appendix needs every type of content. Keep proofs and extra experiments distinct
from implementation instructions when that makes navigation easier.

## Placement and consistency

- Unless a proof is short and straightforward, the corresponding appendix is the
  default home of its complete formal proof. The body retains the full theorem
  statement and assumptions, plus a concise labelled proof sketch and an explicit
  destination such as `Appendix~\ref{app:proof-main}`. Follow the
  [proof-placement rule](09_security_correctness.md#proof-placement) and record any
  exception required by the venue. Do not hide a premise, essential new mechanism,
  failed case or interpretation-changing limitation in the appendix.
- Give specific labels for both directions: the body names the appendix subsection
  containing the proof, and that subsection names the body theorem it proves.
  Restated results preserve numbering and statement content; keep shared source to
  avoid drift. A generic “proofs are in the appendix” is insufficient when readers
  cannot locate the proof of the particular result.
- Tables share their data with the body and retain parameters, units and EVIDENCE
  links. Extra rows must not silently change the headline range or exclusions.
- Reproduction material identifies actual commands, versions and expected outputs.
  Label unchecked instructions honestly; an artifact link is not evidence of a run.
- For separate proceedings/full-version builds, check cross-references in each
  build and identify exactly which version contains the deferred detail. A claimed
  public full version must exist at a stable accessible location. Preparation does
  not authorize publication or upload; follow the project's external-release rule.
- Count body, references and appendices separately and apply the current CFP's
  inclusion rules. Source switches may select permitted material; they must not
  leave a theorem referring to a missing proof without a valid explicit pointer.

## Checklist

- [ ] Every deferred obligation has a precise, available destination.
- [ ] Main premises, scope and essential reasoning remain visible in the body.
- [ ] Statements, symbols, data and cross-references agree across versions.
- [ ] Page counting and supplementary-file rules follow the actual venue.

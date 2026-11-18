# Synthetic overview and positioning examples

All constructions, references and result premises below are hypothetical. They
illustrate exposition; they do not establish a cryptographic result or provide
numerical evidence for a real paper.

## Explain an operation before naming it

Bad:

> Our adaptive witness bridge enables seamless proof composition through a novel
> certificate layer.

Better, for a hypothetical construction with the stated checks:

> The prover commits to the vector before the verifier samples an evaluation
> point. It then supplies a claimed evaluation, which the verifier checks against
> the commitment. The next component receives the commitment and the checked
> evaluation. Its theorem additionally requires that the commitment support the
> extraction property stated in the preliminaries.

Function map: fixed object → challenge order → verification action → output
interface → needed assumption. The text should point to the actual protocol and
theorem. Calling the interface a new “bridge” would not explain any of these steps.

## A failed approach is optional

Use a failed attempt when it explains a specific obstruction. For example, an
approach may reduce one verification step while leaving a list of commitments
that the next step must still process. Explain that surviving obligation, then
the construction's actual change. Do not invent a failure or claim security from
this intuition. An operation-by-operation explanation may be clearer when no
failed attempt is needed.

## Group related work by the actual comparison

Suppose fictional scheme A preprocesses a fixed table, fictional scheme B
supports changing tables, and our hypothetical result assumes a special table
representation. A useful working table is:

| Approach | Supported table setting | Work paid before proving | Question for comparison |
|---|---|---|---|
| A | Fixed table | Per-table preprocessing | How often is the table reused? |
| B | Changing tables | Specified in its construction | Does update cost belong to the measured task? |
| Our result | Tables with the required evaluation property | Representation construction | Are the same inputs supported, and is preprocessing counted? |

This table makes assumptions inspectable without manufacturing a common speedup
or an empty “region” occupied only by our method. A real table needs original
source locators and accepted evidence. Unavailable entries remain unavailable.

## Headings and equations

“Committing before the challenge”, “Updating the accumulated instance” and
“Preprocessing the table” can be informative headings when they describe the
actual argument. There is no requirement to write “Insight 1” or to use a full
sentence as every heading. Include an equation when it specifies a check or
explains why a change works; introduce its domain and symbols first. A simplified
formula must be mapped back to the formal statement with its assumptions intact.

## What intuition does not establish

A sparse representation does not by itself hide its support. A checked polynomial
identity does not by itself supply witness extraction. Fewer commitments do not
by themselves imply lower full-system runtime. The overview should expose the
corresponding obligations and point to their evidence, not rename them away.

# 03 Introduction

## Reader's question and inputs

What task matters here, what specifically limits the relevant approach, and what
does this paper establish? Read the actual construction and theorem scope, accepted
CLAIMS rows, EVIDENCE, and the relevant original literature before framing the gap.
Use [section planning](../references/section-planning.md) and the
[source passage analyses](../references/front-section-patterns.md) for a substantial
rewrite. A routine sentence edit need not create a new literature survey.

## Functional outline

| Function | Content and information dependency |
|---|---|
| Establish the task | Introduce the computation or relation and who proves or verifies it. Give only the application context needed to understand its importance. |
| Explain the relevant approach | State what existing methods actually compute, defer or check. Define unfamiliar objects before using them to describe a weakness. |
| Isolate the difficulty | Identify a precise cost, unsupported setting or proof obligation. Give its parameters, unit and source. Distinguish a local design issue from a field-wide open problem. |
| State the response | Name the contribution type and concrete change; explain how it addresses the stated difficulty. A framework name is optional. |
| Summarise the supported result | Give the guarantee or observation with material assumptions, comparison scope and trade-offs. Link to the construction, theorem or evidence that establishes it. |
| Justify the applicable setting | Explain why a material restriction is compatible with a concrete useful workload, citing a checked mapping or evidence and the costs of any mitigation. If not established, label the extension or gap. |
| Guide the reader | Add contributions, overview, positioning and a roadmap where useful. Their order follows the argument, not fixed subsection numbers. |

A bottleneck-first opening suits a narrowly defined operation; an application-first
opening suits a construction whose computational model needs explanation. Nova's
published introduction moves from IVC and existing recursion to folding; Quasar
separates its commitment-combination target from public-input processing; KiloNova
introduces its machine-execution problem before its folding mechanism. These are
examples, not mandatory narratives.

## Drafting decisions

- Plan paragraphs by function, prerequisites, actual content and support. Analyse
  sentences individually when an unexplained name or missing transition obscures
  the dependency. Do not manufacture an objective equation, pipeline or open
  question to fill a template.
- Include an equation when it makes the task or mechanism more precise. Explain
  its symbols locally; a formal optimisation problem is useful only if the paper
  actually studies that problem.
- Attribute each prior result to its supporting source. There is no citation
  quota or requirement to cite a whole lineage as one block. Prefer the relevant
  published version; identify details taken from a different extended version.
- Use the [shared terminology rules](../references/terminology.md). A rare label
  needs a concrete role and definition, even when a cited paper uses it.
- Describe the actual distinction from close work. Avoid defensive slogans about
  being more than parameter tuning, or claiming an unexplored dimension without
  literature support. A parameter study or negative result may be a valid contribution.
- Keep the introduction readable without the full formalism. Retain assumptions
  that change the meaning of the headline result; defer their formal definitions
  with clear pointers rather than deleting them.

For material restrictions use [limitations and applicability](../references/limitations-and-applicability.md):
explain the useful supported setting as well as the limit, without turning a
possible workaround into a proved application.

## Checklist

- [ ] The reader can identify the task and difficulty before meeting our mechanism.
- [ ] Every historical limitation or open-problem claim has checked support.
- [ ] Claims, numerical scope and important costs agree with the body and abstract.
- [ ] Paragraph order supplies prerequisites; no compulsory equation, question or brand was invented.
- [ ] Close prior work is represented fairly, including the authors' own work.

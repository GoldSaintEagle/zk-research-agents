---
name: polish-writing
description: Use for a final language pass on a paper section, or when translating a Chinese draft into English academic prose. Removes AI-sounding phrasing, tightens sentences, enforces consistent notation and terminology, and never changes numbers, claims or LaTeX semantics.
---

# Polish writing

## Invariants (never violate)

- Do not change numbers, theorem statements, hypotheses, citations, labels or math.
- Do not strengthen claims ("shows" → "proves", "up to" → "always").
- Keep LaTeX commands intact; do not introduce packages.
- Respect an explicit draft freeze. Near a deadline, prefer necessary, verifiable
  corrections and avoid broad restructuring unless the user requested it.
- Output: revised text + a short modification log (what and why) so the author can
  accept/reject each change.
- **ZK term-protection list.** The pairs below name different technical notions. Never
  merge, swap or "unify" them for consistency, and never shorten one into the other:

  | do not interchange | why |
  |---|---|
  | proof ↔ argument | statistical vs computational soundness |
  | zero-knowledge ↔ honest-verifier ZK | malicious vs honest verifier |
  | soundness ↔ knowledge soundness | existence vs extraction of a witness |
  | SNARK ↔ zkSNARK ↔ SNARG | knowledge and/or ZK may not be claimed |
  | succinct ↔ short | succinct also bounds verifier time |
  | transparent ↔ universal setup | no trusted setup vs one reusable trusted setup |
  | proven ↔ conjectured (soundness, proximity) | theorem vs conjecture regime |
  | statistical ↔ computational ZK | different simulator guarantees |

  Do not change the underlying notion in a language pass. Check the actual formal
  definition before editing a protected term. Correct an unambiguous wording error
  within the authorized task and log the reason. If the intended notion cannot be
  determined from the theorem and ledger, retain it and flag the unresolved choice;
  ask only when that ambiguity prevents the requested correction. Routine edits
  around a protected word do not require a separate permission round.

## Before polishing: preserve the paragraph's job

Read the section's existing outline and the relevant
[section guide](../paper-playbook/SKILL.md). For a substantial rewrite use
[section planning](../paper-playbook/references/section-planning.md); for a small
language edit a brief working note is enough. Identify what the paragraph explains,
what prior definitions it needs, and what the next paragraph relies on. Improve
that connection without adding an unsupported claim to make the narrative smoother.

Check first-use explanations and antecedents, especially coefficients, instances,
commitments and witnesses that might name several different objects. A fluent
sentence remains defective if readers cannot tell which object it refers to.
Source-style examples illustrate function, not wording to imitate. Prefer a
concrete verb and object over an unexplained technique name.

Apply [clear exposition and contribution emphasis](../paper-playbook/references/clear-exposition.md).
Split distinct non-obvious problems rather than connecting them with a semicolon.
Preserve the explanatory chain A → B → C: supply a missing bridge from the checked
construction, not an invented inference. Do not delete intermediate objects merely
to shorten a sentence. De-emphasize routine Fiat–Shamir and commit-then-challenge
steps in headline prose while retaining protocol order and security conditions.
If the needed bridge is not supported, flag the gap instead of silently filling it.

## Pass 1 — de-AI

First read the manuscript's working terminology/notation list. For a substantial
terminology revision, follow
[the source-selection and naming rules](../paper-playbook/references/terminology.md):
prefer semantically equivalent terms shared by most relevant independent papers
consulted, prioritising published work. A single paper's unusual name does not
become the default because it is published or user-named. Check competing usage,
attribute necessary source-specific vocabulary, and retain differences in the
security model. Do not replace a precise definition with a familiar but inequivalent
term. Remove gratuitous acronyms, internal revision labels and invented compounds;
use established terms or short ordinary descriptions. Never add a label merely to
make the contribution sound new.

Replace or delete:

| avoid | prefer |
|---|---|
| leverage, utilize | use |
| delve into, explore (as a result) | examine, study (or state the result) |
| pivotal, crucial, paramount | important, key (or delete) |
| underscore, highlight (as filler) | show |
| tapestry, landscape, realm | (delete; name the area) |
| seamless(ly), robust (without a metric) | (delete or quantify) |
| "It is worth noting that", "Notably," | (delete; state the fact) |
| "In this paper, we aim to" | "We ..." |
| "First and foremost", "Last but not least" | (delete) |
| "plays a crucial role in" | "determines", "dominates" (be specific) |
| "novel" about own work | (delete; let the reader judge) |
| "significantly" without numbers | the number |
| "obviously", "it is easy to see" | give the one-line reason, or delete |

Also: convert `itemize` inside running text into connected prose when the items are
reasoning steps (keep lists when they make independent items easier to compare).
Remove redundant connectives. Use a question or descriptive heading only when it
states an actual issue the following text resolves; do not manufacture an Insight
or question merely to fit a template.

## Pass 2 — concision

- Give a sentence a clear main function. Split it when hypotheses, operations and
  conclusions become hard to follow; no universal word limit applies.
- Remove throat-clearing openers and doubled phrases ("in order to" → "to",
  "the fact that" → "that", "a number of" → "several"/the number).
- Prefer verbs over nominalisations ("perform an evaluation of" → "evaluate").
- Active voice for what *we* did; passive is fine for standard facts.
- Avoid dashes as sentence punctuation (use commas, colons, or split sentences).
- Consolidate repeated scope statements and disclaimers where possible. Keep
  assumptions in theorem statements and material limitations beside the affected
  comparison; shorten repetition without deleting those conditions.

## Pass 3 — consistency

- Terminology: one name per concept (framework name, stage names, baseline names).
  Existing terminology takes precedence over manufacturing a new framework name.
  Consistency alone is insufficient: check whether a consistently used rare name
  should instead use a more widely adopted equivalent. Preserve author quotations,
  distinct definitions and exact technical identifiers.
  Build a term list from the notation table and `grep` for variants
  (e.g. "sumcheck"/"sum-check"). Inspect context before replacement: a protocol,
  its underlying relation and its implementation can legitimately have different
  names. Use the protected-term rule above for genuine semantic ambiguity.
- Notation: prefer symbols and conventions inherited from directly relevant
  prior papers, especially the primary baseline, for the same definitions. Follow
  [notation alignment](../paper-playbook/references/terminology.md#align-notation-with-prior-work-and-the-baseline).
  Check the source-to-paper mapping, symbol types and justified deviations; keep
  vectors/matrices, indices and operators consistent across text and appendices.
  Do not introduce new notation for stylistic variety. In a language-only pass,
  flag discrepancies without silently altering math; apply a consistent mapping
  when a notation revision is explicitly within the requested scope.
- Spelling variety: pick US or UK and stay with it.
- Capitalisation of references: `Section~\ref`, `Table~\ref`, or `\Cref` consistently;
  non-breaking spaces before `\cite` and `\ref`.
- Numbers: consistent units and precision (e.g. 2 significant digits for ratios);
  `\times` spacing consistent; thin space before units.

## Pass 4 — Chinese → English (for drafts written in Chinese)

1. Translate meaning, not word order: Chinese topic-comment sentences often become
   English subject-verb sentences with the conclusion first.
2. Split long Chinese sentences joined by commas (一逗到底) into several English
   sentences.
3. Watch for common calques: "has important significance" → "matters because ...";
   "realize/achieve an algorithm" → "implement"; "the proposed scheme" repeated →
   name it once, then "our scheme"/its name; "in recent years" as an opener → delete or
   give the year range; "greatly improve" → the number.
4. Articles: every singular countable noun needs a/the; "the" for things already
   introduced or unique ("the sum-check protocol of [X]").
5. Tense: present for facts and what the paper does; past for what prior work did
   or for experiments that were run.
6. Produce the requested English/LaTeX text and a concise change log. Add a Chinese
   back-translation when requested or useful for resolving meaning. Translate
   protected terms from the actual definition (e.g. 证明 may mean "proof" or
   "argument"); log unresolved ambiguity rather than silently choosing a stronger notion.

## Pass 5 — read-aloud check

Read the edited passage in order, including its preceding definition and following
use. Confirm that the reader can identify the object, follow the argument and find
the supporting result. Reading aloud is optional; short sentences alone do not
establish clarity or technical correctness.

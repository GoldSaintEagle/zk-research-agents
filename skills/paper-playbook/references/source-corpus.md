# Sources for the section-function examples

Status and metadata checked 2026-11-14. The linked pattern files analyse selected
passages, not all sentences or all claims of these works. Page locators below use
one-based PDF pages; do not substitute proceedings numbering for an extended PDF.

| Work | Actual text used for the examples | Publication/version boundary |
|---|---|---|
| Nova | [CRYPTO 2022 published PDF](https://crypto.iacr.org/2022/papers/538806_1_En_13_Chapter_OnlinePDF.pdf), 30 PDF pages = proceedings pp. 359–388 | [Publisher record](https://link.springer.com/chapter/10.1007/978-3-031-15985-5_13); use this published text for the supplied Nova locators. |
| HyperNova | 96-page extended text associated with [ePrint 2023/573](https://eprint.iacr.org/2023/573) | [CRYPTO 2024 publication](https://link.springer.com/chapter/10.1007/978-3-031-68403-6_11), pp. 345–379. The inspected extended text says it incorporates additional material; its appendices/section numbers are not asserted to be those of the proceedings version. |
| Quasar | 55-page public mirror copy titled *Sublinear Multi-Cast Commitment Mixing in Recursive Accumulation* | [Official record](https://eprint.iacr.org/2025/1912) labels it Preprint; latest listed revision 2026-03-18. Observations refer to the inspected copy, not a claim of byte identity with the latest official PDF. |
| KiloNova | 50-page public mirror copy titled *Preprocessing Folding-based SNARKs for Machine Executions* | [Official record](https://eprint.iacr.org/2023/1579) labels it Preprint; latest listed revision 2026-02-17. Do not conflate older titles, anonymous drafts or differing versions. |

The public mirror used for the latter two is `eprint.iacr.asia`; it supplies text,
not peer-review status. Version differences require checking a new source rather
than copying these page locators to another PDF. Public metadata and actual text
take precedence over secondary summaries.

## How these sources inform the skills

- [Front sections](front-section-patterns.md) show how context, definitions,
  contributions, mechanisms and comparisons supply prerequisites to later units.
- [Formal sections and evaluation](formal-section-patterns.md) show how typed
  objects, algorithms, proof obligations and scoped measurements are connected.
- [Abstract analysis](../../abstract-craft/references/sentence-functions.md) retains
  the sentence-level treatment of the user-selected Quasar/KiloNova abstracts.

Observed choices are examples, not prescriptions. No independent proof or
benchmark reproduction is implied by an exposition analysis. This small, related
set does not establish field-wide majority terminology. Follow
[the terminology method](terminology.md) for disputed words, including independent
papers outside a single naming lineage. Routine familiar terms need no new survey.

## Inspected PDF fingerprints

SHA-256 identifies the exact local source text underlying these page locators;
these hashes do not assert latest-version identity.

| Work | SHA-256 |
|---|---|
| nova | 725dae5ae514e19028e52d475aec9d4ab72387dbd730a1503f09edbc1a428f09 |
| hypernova | 08fdc3b155a9b681baecb48aad26993f53c0cb08511c0771154bd5a349761572 |
| quasar | e9b39282c70443ce3f0f912585213e7f097b9982c21a7b3469db38f3021f0aa2 |
| kilonova | 6d84487f4502d56ac175864f1f25bbdd3619b24b0084893515a3747b6f51539d |

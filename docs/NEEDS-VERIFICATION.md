# Open verification items

Every statement in this repository that is still marked `needs verification` (or is a recalled, unchecked
table of contents), in one list. Line numbers are those of the commit that last touched this file; find the
current ones with

```bash
git grep -n -i -E "needs[ -]verification|recalled" -- ':!*.bib' ':!*.json' ':!*.log'
```

Not listed: the places that *define* the marker or the bib-verify statuses (`UNVERIFIED`, `UNCHECKED`, the
"write needs verification" rules in `skills/falsify`, `skills/eprint-search`, `agents/falsifier.md`, the
catalog legends), and synthetic case-study data. Closing an item means: check it against the source named,
replace the marker by the verified fact and its source, and delete the row here.

## Proof-system facts and references

| file:line | open item | how to close it |
|---|---|---|
| `references/books/GLOSSARY.md:68` | multi-adaptive (multi-proof) ZK: defined in neither CY24 nor Thaler | find a paper that defines it; cite it with an ePrint id or DOI checked by bib-verify |
| `skills/zk-definitions/SKILL.md:29` | same notion (top of the ZK hierarchy) | as above |
| `skills/soundness-budget/SKILL.md:66` | what ePrint 2025/2046 and 2025/2197 say about the conjectured RS proximity regime (only titles checked) | read both; state which parameter ranges they cover |
| `skills/soundness-budget/scripts/soundness_calc.py:279` | same two papers in the conjectured-regime docstring | as above |
| `skills/soundness-budget/scripts/soundness_calc.py:288` | grinding term, marked heuristic (ethSTARK documentation, ePrint 2021/582) | check the statement and its assumptions for the way our challenge is derived |
| `skills/soundness-budget/scripts/soundness_calc.py:441` | curve security cap (ePrint 2017/334) | check per curve that the toy KZG budget names |
| `skills/piop-pcs-compile/SKILL.md:93` | exact theorem numbers of the algebraic compiler theorems (Marlin 2019/1047, PLONK 2019/953, HyperPlonk 2022/1355) | open each paper; cite the theorem number used |
| `case-study/toy-rangecheck/MATH-REFS.md:12` | lemma number of the logarithmic-derivative lemma in logUp (ePrint 2022/1530) | open the paper; fill in the number (teaching example) |
| `figures/PATTERNS.md:40` (and every "Candidates:" line) | whether each candidate paper actually contains a figure of that pattern | open the paper; keep it only if the figure fits, or re-run the harvester on a ZK corpus |

## Tools and their output formats

| file:line | open item | how to close it |
|---|---|---|
| `skills/circuit-audit/SKILL.md:94` | halo2 `MockProver` failure categories for the halo2 version we pin | run MockProver on a failing toy circuit at the pinned version |
| `skills/circuit-audit/SKILL.md:95` | Circomspect's current list of checks | read the current Circomspect README / source |
| `skills/circuit-audit/SKILL.md:96` | Picus front ends beyond Circom / R1CS | read the current Picus README |
| `skills/constraint-cost/SKILL.md:97` | constraint counts of any specific non-native-arithmetic gadget library | take the number from that library's own output, with its version |
| `skills/constraint-cost/SKILL.md:134` | exact compiler commands and output formats (circom, snarkjs, gnark, halo2, nargo) | run each at the pinned version; paste the real output |
| `lib/bench/crbench/parsers.py:24` | general note: formats reconstructed from public logs | the rows below |
| `lib/bench/crbench/parsers.py:239`, `lib/bench/README.md:48`, `lib/bench/tests/test_parsers.py:100` | snarkjs verify line `snarkJS: OK!` | run `snarkjs groth16 verify` once |
| `lib/bench/crbench/parsers.py:259`, `lib/bench/README.md:49`, `lib/bench/tests/test_parsers.py:116` | rapidsnark builds with optional logging | build with logging enabled; capture output |
| `lib/bench/crbench/parsers.py:271`, `lib/bench/README.md:50`, `lib/bench/tests/test_parsers.py:124` | circom compile summary (no sample in the official docs) | `circom --r1cs` on a toy circuit |
| `lib/bench/README.md:51`, `lib/bench/tests/test_parsers.py:136` | gnark compile-time `nbConstraints` log line | compile a toy gnark circuit with logging |
| `lib/bench/README.md:53`, `lib/bench/tests/test_parsers.py:177` | older `nargo info` column layouts | run an older nargo release, or drop the old layout |
| `lib/bench/crbench/parsers.py:358`, `lib/bench/README.md:54` | older RISC Zero `total cycles` / `user cycles` lines | run an older release, or drop the old format |
| `lib/bench/crbench/parsers.py:385`, `lib/bench/README.md:55`, `lib/bench/tests/test_parsers.py:203` | SP1 `Number of cycles:` variant | run the pinned SP1 example scripts |

## Baselines (`references/baselines/MANIFEST.md`)

| file:line | open item |
|---|---|
| `references/baselines/MANIFEST.md:88` | halo2-pse criterion bench names |
| `references/baselines/MANIFEST.md:93` | lambdaworks per-crate benches |
| `references/baselines/MANIFEST.md:94` | Expander: MPI for multi-process runs, bench binary and flags, output format |
| `references/baselines/MANIFEST.md:95` | binius64 example output format |
| `references/baselines/MANIFEST.md:96` | whether IrreducibleOSS/binius is superseded by binius64 |
| `references/baselines/MANIFEST.md:97` | Stwo criterion bench names |
| `references/baselines/MANIFEST.md:98` | ICICLE GPU benches per backend; criterion for the Rust wrappers |
| `references/baselines/MANIFEST.md:108` | barretenberg build, `bb prove` flags; whether the repository mirrors aztec-packages |
| `references/baselines/MANIFEST.md:115` | SP1 `cargo prove build` for this release |
| `references/baselines/MANIFEST.md:127` | Sonobe examples / benches and their parser |

Close each by building at the pinned tag (`references/baselines/fetch.sh`) and recording the real command and
output; crbench has no Jolt parser yet (Jolt writes `summary.json`).

## Formalisation (`skills/lean-bridge/SKILL.md`)

| file:line | open item |
|---|---|
| `skills/lean-bridge/SKILL.md:43–46` | which of the listed CY24 results ArkLib already proves, and in which form (FS bound and input notion at :45, RBR ⇒ SR at :46) |
| `skills/lean-bridge/SKILL.md:68` | VCV-io URL and current API |
| `skills/lean-bridge/SKILL.md:69` | Mathlib lemma names (`Polynomial.card_roots'`, `MvPolynomial.schwartz_zippel_*`) at the pinned Mathlib revision |

## Books and venues

| file:line | open item |
|---|---|
| `references/textbooks/CATALOG.md:61` | Guruswami–Rudra–Sudan, *Essential Coding Theory*: draft date / version |
| `references/textbooks/CATALOG.md:62` | Roth, *Introduction to Coding Theory*: edition / year |
| `references/textbooks/CATALOG.md:63` | MacWilliams–Sloane: year |
| `references/textbooks/CATALOG.md:64` | Guruswami, *Algorithmic Results in List Decoding*: venue / year |
| `references/textbooks/CATALOG.md:65` | Guruswami–Sudan RS list decoding: venue / year |
| `references/textbooks/toc/boneh-shoup-graduate-course-in-applied-cryptography.md:5` | chapter-level TOC recalled from a public source |
| `references/textbooks/toc/katz-lindell-introduction-to-modern-cryptography.md:5–6` | chapter-level TOC recalled (3rd edition order) |
| `references/textbooks/toc/lidl-niederreiter-finite-fields.md:5` | chapter-level TOC recalled |
| `skills/venue-calibration/SKILL.md:30` | AFT proceedings series (LIPIcs in recent years) |

## Left out on purpose (no verifiable record yet)

`references/reading-lists/README.md` lists papers kept out of the reading lists until they have a DOI or a
URL-source entry: the Chaliasos et al. SoK on SNARK vulnerabilities, the RISC Zero / SP1 write-ups, the
TinyRAM specification, Chiesa–Tromer PCD (ICS 2010), Ecne and Circomspect.

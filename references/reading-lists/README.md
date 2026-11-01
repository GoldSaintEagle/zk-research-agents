# Reading lists

Curated, public-only starting points for ZK research, one list per direction. Each list is a `.md`
(scope, suggested reading order, a table with a one-line "why read") and a `.bib` with the same name
(drop-in BibTeX). They are a seed for `lit-scout`, not a survey.

Every entry was resolved on 2026-11-01 by `skills/bib-verify/scripts/verify_bib.py` and is `VERIFIED`
(title, authors, year) against its **DOI** record (Crossref or DataCite). On that date eprint.iacr.org
refused this machine and DBLP served a bot challenge, so:

- every entry carries a `doi`; the DOI is the published (or full journal) version, which is the version
  a paper should cite anyway;
- no `eprint=` ids are recorded yet — add them after a verifier run that can reach ePrint;
- important papers that exist only on ePrint (e.g. PLONK, Plookup, cq, logUp, CCS, SuperNova, CycleFold,
  Halo, ProtoGalaxy, Cairo) are **not** in the lists: they could not be verified, and the rule below
  keeps unverified entries out. The candidates are listed in the hand-over notes of the batch that
  built the lists; add them once they verify.

| list | scope | entries |
|---|---|---|
| [pcs](pcs.md) | polynomial commitments: KZG and multilinear-from-univariate, inner-product / DARK, RS proximity (FRI, STIR, WHIR), linear-code PCS (Ligero, Brakedown, BaseFold, Blaze) | 18 |
| [piop-arithmetization](piop-arithmetization.md) | IOPs and PIOP compilers, sum-check / GKR provers, linear PCPs and Groth16, AHPs, STARK/AIR, multilinear PIOPs | 14 |
| [lookup](lookup.md) | lookup and memory-checking arguments: KZG / table-independent line, Lasso, Twist and Shout, folding lookups | 8 |
| [folding-recursion](folding-recursion.md) | IVC and PCD, cycles of curves, accumulation, Nova-family folding | 14 |
| [zkvm](zkvm.md) | RAM-to-circuit reductions, TinyRAM, memory checking, RAM-model ZK, Jolt, Ceno, folding-based zkVMs | 12 |
| [fiat-shamir-soundness](fiat-shamir-soundness.md) | Fiat–Shamir, forking, random-oracle caveats, attacks on FS, correlation intractability, round-by-round and state-restoration soundness, proximity gaps and FRI concrete soundness | 19 |
| [circuit-security](circuit-security.md) | circuit languages and compilers, under-constraint detection, formal verification, testing and fuzzing of circuits | 14 |
| [pq-and-hash-based-zk](pq-and-hash-based-zk.md) | MPC-in-the-head and VOLE-in-the-head, ZK-based signatures (Picnic, Banquet, Limbo, SDitH), quantum-ROM security of succinct arguments, lattice-based arguments | 14 |

**Why these eight directions.** They follow the plan's split of the old `zk-proofs` list (PCS, PIOP,
lookup, folding, zkVM, FS soundness, circuit security, PQ-ZK) and map onto the skills that consume them:
`piop-pcs-compile` (pcs, piop-arithmetization), `constraint-cost` (lookup), `prover-cost-model`
(pcs, zkvm), `soundness-budget` and `fiat-shamir-audit` (fiat-shamir-soundness), `circuit-audit`
(circuit-security). PIOP and arithmetization share one list because the arithmetization (R1CS, AIR,
Plonkish, CCS) is defined together with the PIOP that proves it. Hash-based arguments that are mainly
commitment schemes sit in `pcs`; `pq-and-hash-based-zk` keeps the post-quantum-specific lines and
absorbs the ZK part of the former post-quantum signatures list.

**One home per paper.** A paper central to two directions is listed once; the other list names it in
its suggested order as `KEY [in <list>]` and in an "Also part of this direction" line.

**Sources.** Candidates come from Crossref searches and from the
bibliographic notes of the reference books ([CY24 §Bibliographic notes, section:bibliographic-notes] and
Thaler's bibliography, see `references/books/`); only the bibliographic data is taken, never the
books' commentary.

Rules for extending a list:

1. Public references only; give the DOI (published version) and, once verified, the ePrint id in `eprint=`.
2. Anything you are not sure exists goes in with a `% UNVERIFIED` comment line directly above it, and
   leaves the list before it is committed unless the verifier confirms it.
3. Run `python3 skills/bib-verify/scripts/verify_bib.py <list>.bib` and fix every non-`VERIFIED` row.
   `UNCHECKED` (service error, blocked) is not a pass: re-run until the row resolves. Never copy authors,
   DOIs or ePrint numbers from memory — copy them from the record the verifier matched.
4. Keep a list under ~25 entries; spin off a new list rather than growing one. Keep one home per paper.

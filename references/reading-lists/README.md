# Reading lists

Curated, public-only starting points for ZK research, one list per direction. Each list is a `.md`
(scope, suggested reading order, a table with a one-line "why read") and a `.bib` with the same name
(drop-in BibTeX). They are a seed for `lit-scout`, not a survey.

Every entry was checked on 2026-11-01 by `skills/bib-verify/scripts/verify_bib.py`. On that date
eprint.iacr.org refused this machine (HTTP 302 to the IACR block notice) and DBLP served a bot
challenge, so:

- an entry with a DOI is `VERIFIED` (title, authors, year) against its **DOI** record (Crossref or
  DataCite); the DOI is the published (or full journal) version, which a paper should cite anyway, and
  no `eprint=` is recorded for these entries yet;
- an entry that exists only on ePrint (PLONK, Plookup, cq, logUp, CCS, SuperNova, CycleFold, Halo,
  Cairo, ...) carries `eprint=` and the official `url = https://eprint.iacr.org/YYYY/NNNN`, and is
  was first `VERIFIED (mirror)`: it matched the record of the **third-party** mirror
  https://eprint.iacr.asia (not run by the IACR), which the verifier uses only when the official site is
  unusable and the entry has no DOI. On 2026-11-03 eprint.iacr.org answered again and all 23 of these
  rows were re-checked against it with `verify_bib.py --require-official`: all `VERIFIED`;
- all 139 entries are `VERIFIED` (116 through a DOI, 23 against official ePrint), none in any other state.

Papers still left out: the Chaliasos et al. SoK on SNARK vulnerabilities (USENIX Security 2024; not on
ePrint according to the mirror, no DOI), the RISC Zero / SP1 write-ups and the TinyRAM specification
(not on ePrint), Chiesa–Tromer PCD (ICS 2010), and the tools Ecne and Circomspect (no paper record);
they need a URL-source entry or a DOI before they can be added.

| list | scope | entries |
|---|---|---|
| [pcs](pcs.md) | polynomial commitments: KZG and multilinear-from-univariate, inner-product / DARK, RS proximity (FRI, STIR, WHIR), linear-code PCS (Ligero, Brakedown, BaseFold, Blaze) | 20 |
| [piop-arithmetization](piop-arithmetization.md) | IOPs and PIOP compilers, sum-check / GKR provers, linear PCPs and Groth16, Sonic and PLONK, CCS, AHPs, STARK/AIR, multilinear PIOPs | 18 |
| [lookup](lookup.md) | lookup and memory-checking arguments: Plookup, Caulk / cq / KZG table-independent line, logUp and logUp-GKR, Lasso, Twist and Shout, folding lookups | 15 |
| [folding-recursion](folding-recursion.md) | IVC and PCD, cycles of curves, Halo and accumulation, Nova-family folding (SuperNova, CycleFold, ProtoGalaxy) | 21 |
| [zkvm](zkvm.md) | RAM-to-circuit reductions, TinyRAM and vnTinyRAM, Cairo, memory checking, RAM-model ZK, Jolt, Ceno, folding-based zkVMs | 15 |
| [fiat-shamir-soundness](fiat-shamir-soundness.md) | Fiat–Shamir, forking, random-oracle caveats, attacks on FS, correlation intractability, round-by-round and state-restoration soundness, proximity gaps and FRI concrete soundness | 20 |
| [circuit-security](circuit-security.md) | circuit languages and compilers, under-constraint detection, formal verification, testing and fuzzing of circuits | 15 |
| [pq-and-hash-based-zk](pq-and-hash-based-zk.md) | MPC-in-the-head and VOLE-in-the-head, ZK-based signatures (Picnic, Banquet, Limbo, SDitH), quantum-ROM security of succinct arguments, lattice-based arguments | 15 |

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
   An ePrint-only paper gets `eprint=`, `howpublished = {Cryptology ePrint Archive, Paper YYYY/NNNN}` and
   `url = {https://eprint.iacr.org/YYYY/NNNN}` — the official canonical URL, never a mirror URL.
2. Anything you are not sure exists goes in with a `% UNVERIFIED` comment line directly above it, and
   leaves the list before it is committed unless the verifier confirms it.
3. Run `python3 skills/bib-verify/scripts/verify_bib.py <list>.bib` (rate-limited; one list at a time) and fix
   every row that is neither `VERIFIED` nor `VERIFIED (mirror)`.
   `UNCHECKED` (service error, blocked) is not a pass: re-run until the row resolves. Never copy authors,
   DOIs or ePrint numbers from memory — copy them from the record the verifier matched.
4. Keep a list under ~25 entries; spin off a new list rather than growing one. Keep one home per paper.

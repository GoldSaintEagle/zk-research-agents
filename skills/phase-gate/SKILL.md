---
name: phase-gate
description: Evaluate whether a research project may leave phase P0..P8 by checking the STATE.md gate checklist, CLAIMS.md verdicts, EVIDENCE.md coverage of paper numbers, and bib-verify status. Use at every phase transition and before any external submission.
---

# phase-gate

The orchestrator owns gates; this skill is the checklist and the mechanical checker.

## Mechanical check

```bash
python3 skills/phase-gate/scripts/gate_check.py --project . --phase P6
python3 skills/phase-gate/scripts/gate_check.py --project . --phase P7 --paper paper/
python3 skills/phase-gate/scripts/gate_check.py --selftest
```

It fails on: unticked gate items (waivers need `WAIVED: <reason> (DECISIONS D-<n>)`), `open` claims from P6 on,
`survived`/`weakened` claims without EVIDENCE refs or falsifier evidence, paper numbers (×, %, ms, kB/KiB, bits,
bits of security, constraints, rows, gas, cycles, 2^k …)
without a matching EVIDENCE row from P7 on (escape hatch: `% no-evidence: <reason>` on the line — crbench's
`% crbench:ignore` and its begin/end blocks count too, and crbench accepts `% no-evidence:` — e.g. a number quoted
from a cited paper), and a missing/stale/unclean bib-verify report at P8.

## Gate checklists (copy into STATE.md under `## Gate P<k>`)

The same items as the gate column of `workflows/PHASES.md` and the table in `agents/pi-orchestrator.md`
(and its zh mirror); change all of them together.

**P0 Scoping** — [ ] thesis is one falsifiable sentence ·
[ ] paper type (protocol / system / application) and the agents it needs ·
[ ] measurable target + baseline value ·
[ ] venue CFP read + deadline ·
[ ] in/out-of-scope list ·
[ ] compute/time budget ·
[ ] kill date and kill criteria.

**P1 Literature** — [ ] related-work matrix with ≥ 15 verified works incl. the 2–4 true competitors ·
[ ] strongest baseline named ·
[ ] novelty / pre-emption check (ePrint + grey literature) ≤ 14 days old, verdict ≠ taken ·
[ ] refs.bib passes bib-verify ·
[ ] reading notes per competitor ·
[ ] baseline candidates with code status.

**P2 Ideation** — [ ] ≥ 1 idea with a cost-model gain (constraint-cost / prover-cost-model / piop-pcs-compile) and a kill criterion ·
[ ] Gate A + Gate B recorded (or honest negative) ·
[ ] top idea registered as falsifiable CLAIMS rows ·
[ ] novelty re-check of the chosen idea.

**P3 Theory** — [ ] every lemma numerically checked on small params (`sage-check`) ·
[ ] main theorem proof complete (soundness notion, model and setup explicit; [zk-definitions](../zk-definitions/SKILL.md) assumption ledger) ·
[ ] soundness budget table with every term marked proven or conjectured and the level definition named ([soundness-budget](../soundness-budget/SKILL.md)) ·
[ ] lower bound or "none known".

**P4 Baselines** — [ ] strongest baseline builds at a pinned commit ·
[ ] its published numbers reproduced within tolerance or the discrepancy documented ·
[ ] every competitor signed off at the same soundness level as ours (bits, proven/conjectured regime, level definition) ·
[ ] build configuration identical to `impl/BUILD.md` or the differences recorded.

**P5 Experiments** — [ ] protocol fixed before running ·
[ ] interleaved runs, ≥ 3 repeats, medians ·
[ ] environment captured ·
[ ] every timed run verified its proof ·
[ ] every candidate paper number (times, sizes, constraint counts) has an EVIDENCE row ·
[ ] prediction vs measurement compared phase by phase ([prover-cost-model](../prover-cost-model/SKILL.md)).

**P6 Falsification gate** — [ ] no `open` claims ·
[ ] refuted claims removed from narrative, weakened wording adopted ·
[ ] soundness budget recomputed independently by the falsifier ·
[ ] Fiat–Shamir audit ([fiat-shamir-audit](../fiat-shamir-audit/SKILL.md)) and circuit audit ([circuit-audit](../circuit-audit/SKILL.md)) passed in the falsifier's own re-run (the builders' self-audits do not count) ·
[ ] price of each gain stated ·
[ ] PI decision logged.

**P7 Writing + figures** — [ ] playbook sections complete ·
[ ] every number ↔ EVIDENCE row (`crbench audit-tex` passes) ·
[ ] every claim ↔ survived/weakened CLAIMS row ·
[ ] 0 undefined refs ·
[ ] figures from logged data by script in house style ·
[ ] related work from the matrix.

**P8 Review → submit → rebuttal → camera-ready** — [ ] mock-review action items closed ·
[ ] bib-verify clean ·
[ ] anonymisation (`anon_check`) and page limit ·
[ ] checklist done ·
[ ] artifact builds clean ·
[ ] final novelty re-check ≤ 7 days old.

## Loops

P6 may send work back to P2 (idea refuted), P3 (proof gap), or P5 (measurement gap). P8 may send back to P7 or P5.
Every backward transition is a DECISIONS.md entry with the triggering claim/review id.

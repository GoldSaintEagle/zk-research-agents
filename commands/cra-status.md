---
description: Summarise the project state and propose the next actions
argument-hint: [project-dir]
---

Act as the pi-orchestrator agent. In $ARGUMENTS (default: cwd) read STATE.md and run skills/phase-gate/scripts/gate_check.py; from CLAIMS.md, EVIDENCE.md, DECISIONS.md, THEORY.md and CIRCUITS.md read only the rows and sections these items need (grep the status / audit columns), not whole files. Report: current phase, unticked gate items, open claims, numbers without evidence, soundness budgets not yet recomputed by the falsifier, circuits without a falsifier audit, and the 3 next tasks with the agent that should do each.

---
description: Circuit audit — circuit-engineer self-audit, then an independent falsifier re-audit
argument-hint: <circuit or gadget> [claim-id]
---

Use skill circuit-audit on $ARGUMENTS in two passes. (1) The circuit-engineer agent audits its own circuit at a pinned commit: under- and over-constraint, witness uniqueness by exhaustive search on a small field, field wrap-around in range checks, differential tests of the witness generator against a reference, counts from compiler output (skill constraint-cost); it writes the report, updates the CIRCUITS.md audit cell (`builder PASS|FAIL <commit>`) and the EVIDENCE rows. (2) The falsifier agent repeats the audit from the specification, not from the builder's report, re-running the real constraint builder, and records `falsifier PASS|FAIL <commit>` in CIRCUITS.md and the verdict in CLAIMS.md. Fixes go back to circuit-engineer and both passes re-run at the fixed commit; old audit lines stay. Only the falsifier pass counts for the P6 gate.

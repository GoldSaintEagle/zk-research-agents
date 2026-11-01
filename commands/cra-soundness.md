---
description: Concrete soundness budget, computed by theorist and recomputed independently by falsifier
argument-hint: <protocol / parameter set> [claim-id]
---

Use skill soundness-budget for $ARGUMENTS in two independent passes. (1) The theorist agent states the notion and the level definition (worst-case or average-case; skill zk-definitions), lists every term (algebraic, PCS proximity, Merkle, hash chain, grinding) with its regime (proven / conjectured / heuristic) and source, computes the bits with skills/soundness-budget/scripts/soundness_calc.py, writes the table into THEORY.md "Parameters and security" and adds the EVIDENCE row. (2) The falsifier agent then rebuilds the budget from the protocol description and parameters, without reading the theorist's table, and compares term by term; any disagreement or a conjectured term presented as proven goes into the claim's CLAIMS.md row (falsifier evidence) and back to the theorist. Done when both budgets agree and every number has an EVIDENCE row.

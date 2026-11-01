---
description: Red-team all open claims
argument-hint: [claim-id]
---

Use the falsifier agent with skill falsify on claim $ARGUMENTS (or every open claim in CLAIMS.md). Attack from three lenses — definitions and model (zk-definitions), Fiat–Shamir and soundness budget (fiat-shamir-audit, soundness-budget, recomputed independently), fairness and precedent (baseline-pin, eprint-search incl. grey literature) — plus circuit-audit for circuit claims. Write scripts under falsify/<id>/, record verdicts survived/weakened/refuted with evidence; a claim whose attacks produced no evidence stays open. For a multi-agent round use workflows/falsify-round.js.

---
description: Fiat–Shamir audit of our protocol (paper and implementation), self-audit then independent re-run
argument-hint: <protocol or impl path> [claim-id]
---

Use skill fiat-shamir-audit on $ARGUMENTS, both as written in the paper (THEORY.md) and as implemented (impl/ or circuits/ for in-circuit verifiers). Check every item of the skill's checklist: statement and public inputs in the first hash, every commitment absorbed before its challenge, domain separation, challenge space and field (extension where the bound needs it), the FS variant and the theorem it relies on (RBR / special / state-restoration soundness proven in THEORY.md), and the multi-round loss in the soundness budget. The builder (prover-engineer for impl/, theorist for the paper) runs it first; the falsifier agent then re-runs it independently and writes falsify/<claim-id>/fs-audit.md in the skill's report format, linked from the claim's CLAIMS.md row. Use skills/fiat-shamir-audit/scripts/toy_fs_attack.py to demonstrate a finding on a toy instance.

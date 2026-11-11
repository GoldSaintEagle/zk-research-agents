---
description: Venue-calibrated mock review
argument-hint: <venue> [protocol|system|application]
---

Use the reviewer-sim agent with skills venue-calibration and mock-review for venue $ARGUMENTS on paper/main.pdf. Personas from skill mock-review — soundness reviewer (proofs and Fiat–Shamir), implementation-and-benchmark reviewer, application-and-industry-relevance reviewer, with the one mandatory for the paper type first, plus the optional data and desk-reject auditors. Verify every high/med finding before it counts (low ones are listed as unverified), write the meta-review into REVIEWS.md and the fix list into reviews/SUBMIT-FIXES.md with action items routed to agents. For a multi-agent round use workflows/mock-review-panel.js.

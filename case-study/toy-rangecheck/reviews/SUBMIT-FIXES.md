# SUBMIT-FIXES — round R1 (from REVIEWS.md)

| grade | id | file | old → new | why |
|---|---|---|---|---|
| must-fix | D-W1 | paper/sections/abstract.tex, intro.tex | "3.69×–3.98× … for 16 ≤ k ≤ 63" → "3.69×–3.81× at the grid points 16 ≤ k ≤ 48 (3.98× at k = 64, outside the range-check domain)" | integrity: number outside the claimed domain |
| must-fix | D-W1 | CLAIMS.md C4 | weakened wording re-issued by the falsifier | paper text must match the ledger |
| should-fix | D-W2 | intro.tex | "for k ≥ 16" → "for 16 ≤ k ≤ 63" | consistency with C3 |
| should-fix | A-W2 | experiments.tex + EVIDENCE E40–E43 | words → numbers with EVIDENCE rows | reproducibility |
| should-fix | I-W1 | experiments.tex | add the PCS limitation (both directions) | persuasiveness |
| should-fix | S-W1/S-W2 | security.tex | theorem sentence | precision of statements |
| must-fix | X-W1 | intro.tex | rephrase the overfull line | compliance |
| won't-fix | A-W3, I-W3 | — | — | see REVIEWS.md |
Good news (checked and correct): every number has an EVIDENCE row; both level definitions named; the circuit
lemma checked exhaustively; refuted claims C1, C5, C7 are absent from the narrative.

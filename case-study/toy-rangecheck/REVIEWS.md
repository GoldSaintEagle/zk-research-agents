# REVIEWS — mock and real reviews (owner: `reviewer-sim`)

## Round R1 — 2026-11-02 — venue profile: mock LNCS workshop short paper — paper hash 5307267c635d
| persona | score | confidence | top-3 weaknesses | action item → agent |
|---|---|---|---|---|
| Application and industry-relevance (mandatory) | 4/6 weak accept | 3/4 | A-W1 no proof size / verifier cost; A-W2 only one statement size in the main grid; A-W3 "lookups win" folk belief not sourced | A-W2 → experimenter + writer (quote the edge runs with EVIDENCE rows); A-W1 → writer (state why not reported); A-W3 won't-fix |
| Soundness (proofs and Fiat–Shamir) | 4/6 weak accept | 3/4 | S-W1 the toy argument's guarantee is only sketched, notion/model not stated in the body; S-W2 "Fiat–Shamir costs a factor t plus the number of rounds" is informal | S-W1, S-W2 → writer (theorem sentence with notion, model, theorem cited) |
| Implementation and benchmark | 3/6 borderline | 3/4 | I-W1 no polynomial commitment: commitment cost per column is underestimated, which flatters the arm with fewer columns (bits); I-W2 the edge runs are mentioned without numbers; I-W3 Table 1 omits k = 24, 48 | I-W1 → writer (limitation, both directions); I-W2 = A-W2; I-W3 won't-fix (figure has them; counts.log complete) |
| Data auditor (optional) | — | 4/4 | D-W1 abstract and intro print "3.69×–3.98× for 16 ≤ k ≤ 63", but 3.98× is the k = 64 point, outside the range-check domain; CLAIMS C4's weakened wording has the same slip ("3.7× to 4.0×"); D-W2 intro says "8× fewer rows for k ≥ 16" while C3 says 16 ≤ k ≤ 63 | D-W1 → falsifier (re-word C4) then writer; D-W2 → writer |
| Desk-reject auditor (optional) | — | 4/4 | X-W1 one overfull box (2.9 pt, intro); X-W2 anonymity not yet checked (anon_check) | X-W1 → writer; X-W2 → submission-rebuttal |

Scope and limits of this review: the PDF, CLAIMS.md, EVIDENCE.md and the logs they cite were read; the benchmark
was not re-run. Personas are views of one analysis, not independent experts.

## Reviewer A — Application and industry relevance
Summary: a careful, explicitly toy measurement of the lookup-vs-bits trade-off, with two audit stories that
practitioners will recognise. The scope is narrow (one backend, one n).
Strengths: S1 the table-height floor is shown, not asserted; S2 both bugs are realistic and their detection
method is given; S3 claims are scoped to what was measured.
Weaknesses: A-W1 (med, §5) no proof size or verifier cost — deployments care; A-W2 (med, §5 "Limb width")
edge runs described in words only; A-W3 (low, §1) folk belief not sourced.
Questions: Q1 would table-independent lookups (cq) remove the small-k loss? Q2 does the loss at k = 4 survive a real PCS?
Scores: overall 4/6, confidence 3/4. Recommendation: weak accept if A-W2 is fixed.

## Reviewer B — Soundness
Summary: the circuit lemma is correct and checked; the argument's guarantee is described in prose only.
Strengths: S1 both level definitions reported, recomputed independently; S2 the FS failure is explained with the
right theorem (statement not hashed → non-adaptive only); S3 k = 64 excluded for the right reason.
Weaknesses: S-W1 (med, §4) no statement of what the toy argument guarantees (notion, model, oracle access);
S-W2 (low, §4) the FS loss is stated informally.
Scores: overall 4/6, confidence 3/4. Recommendation: weak accept.

## Reviewer C — Implementation and benchmark
Summary: same-backend comparison with interleaved runs and verified proofs; the missing PCS biases the comparison
in a direction the paper does not discuss.
Weaknesses: I-W1 (high, §3/§5) with a real PCS each committed column costs commitment work proportional to the
height, so the lookup arm's extra columns cost more than here, while its smaller height costs less: the paper
should say the ratio could move either way; I-W2 = A-W2; I-W3 (low) Table 1 subset.
Scores: overall 3/6, confidence 3/4. Recommendation: borderline; accept with I-W1 stated.

## Meta-review (simulated discussion)
Scores 4 / 4 / 3. Consensus: the measurement is honest and scoped; one confirmed numeric inconsistency (D-W1) is a
must-fix; the missing-PCS limitation must be stated. Decisive issues: D-W1, I-W1, A-W2. Subjective band: accept
at a workshop after the must-fix items. Rebuttal preparation: Q1 (cq), Q2 (real PCS), "why not n = 1024".

## Verified findings
| id | finding | status | evidence (script/log) |
|---|---|---|---|
| D-W1 | 3.98× (E17) is k = 64, outside 16 ≤ k ≤ 63 | confirmed | results/bench_kscan/summary.log; CLAIMS C4 |
| D-W2 | "k ≥ 16" vs C3's 16 ≤ k ≤ 63 | confirmed | paper/sections/intro.tex |
| A-W2 / I-W2 | edge runs not quoted | confirmed | results/falsify_C4_edges/summary.log |
| I-W1 | no PCS: commitment cost per column underestimated | confirmed (by construction) | impl/toy_prover.py docstring |
| S-W1 | no theorem statement for the toy argument | confirmed | paper/sections/security.tex |
| X-W1 | overfull box 2.9 pt | confirmed | paper/pdf-checks.log |
| A-W3 | folk belief unsourced | won't-fix: stated as the hypothesis being tested, not as a citation | — |
| I-W3 | Table 1 omits k = 24, 48 | won't-fix: figure and counts.log have all points | results/counts/counts.log |

## Action items (routing, DECISIONS D-8) and status
| item | agent | status |
|---|---|---|
| D-W1 re-word C4 (16 ≤ k ≤ 48 grid points: 3.69×–3.81×; 3.98× at k = 64 reported separately) | falsifier | closed (CLAIMS.md C4, falsify/votes.json, tally.log) |
| D-W1, D-W2 fix abstract / intro / evaluation wording | writer | closed |
| A-W2 / I-W2 EVIDENCE rows for the edge runs (E40–E43) and quote them | experimenter → writer | closed |
| I-W1 limitation: no PCS, ratio may move either way | writer | closed |
| S-W1, S-W2 theorem sentence (soundness, ROM, oracle access; RBR → SR theorem cited) | writer | closed |
| X-W1 overfull box | writer | closed |
| X-W2 anonymity check | submission-rebuttal | closed (paper/anon-check.log) |

After the fixes the data auditor and desk-reject personas were re-run (skills/mock-review step 7): no open item.

export const meta = {
  name: 'cra-mock-review',
  description: 'Falsify-first ZK mock review (skills/mock-review): personas by paper type, findings verified, meta-review with fixes routed to agents',
  whenToUse: 'Phase P8 before submission (about 3 days and again 1 day before), and after each major revision',
  phases: [{ title: 'Brief' }, { title: 'Review' }, { title: 'Verify' }, { title: 'Meta' }],
}
// args: { project: "/abs/path", venue: "EUROCRYPT", pdf: "paper/main.pdf",
//         paper_type: "protocol" | "system" | "application", extra: ["data-auditor", "desk-reject"] }
const P = args.project, V = args.venue, PDF = args.pdf || 'paper/main.pdf'

// ---- pure functions (workflows/tests/run-tests.mjs loads the block between the markers) ----
// BEGIN PURE
// Personas and checks follow skills/mock-review/SKILL.md (table "Personas" and "Frequent catches").
const PERSONAS = {
  soundness: 'Soundness reviewer (proofs and Fiat–Shamir): a senior theorist who assumes the proof is wrong. Checks: ' +
    'the notion proven vs the notion claimed (soundness vs knowledge soundness vs witness-extended emulation; HVZK vs ZK; ' +
    'adaptive vs non-adaptive; simulation-extractability); the extractor really extracts (rewinding bound, PCS extraction, ' +
    'decoding radius); the simulator covers every PCS opening and query; model, setup and every conjecture in the theorem ' +
    'statement; Fiat–Shamir transcript complete (statement and public inputs hashed) and the multi-round loss accounted for ' +
    '(RBR or SR soundness, not plain soundness); the concrete soundness table recomputed term by term with ' +
    'skills/soundness-budget, proven and conjectured separated, under a named worst-case / average-case level definition; ' +
    'for hash-based arguments the Merkle and hash-chain terms present, not only the IOP term; challenges drawn from the ' +
    'field the bound needs (extension, not base); hypotheses vs the paper\'s own parameter table; small-field ' +
    'counterexamples; body vs appendix formula mismatches. Book anchors for these checks are listed in the soundness rows ' +
    'of "Frequent catches" in skills/mock-review/SKILL.md (CY24 / Thaler references); cite them by label in findings. ' +
    'For an application paper also read the circuit-correctness argument.',
  implementation: 'Implementation and benchmark reviewer: builds provers for a living. Checks: baseline is the current ' +
    'release of the strongest system, pinned; same soundness level and regime on both arms; same statement (not the same ' +
    'constraint count across arithmetizations); identical timing scope (witness generation, preprocessing, setup); same ' +
    'threads and hardware features (AVX-512 / asm / GPU); prover time, verifier time, proof size and memory all reported; ' +
    'recursion / wrapping listed separately; every timed proof verified; prover-phase breakdown explains the gain; scaling ' +
    'over sizes, not one point; artifact builds and runs.',
  application: 'Application and industry-relevance reviewer: a practitioner from a team deploying ZK. Checks: the ' +
    'statement matches a real use (credentials, rollups, zkVMs, ML); trust model (who runs setup, who holds the witness, ' +
    'what is public); on-chain cost (gas, calldata) if claimed; circuit correctness (under-constraint, range checks, field ' +
    'wrap-around) argued, not assumed (skills/circuit-audit); novelty vs the closest prior work including grey literature ' +
    '(project docs, blog posts, production systems); "first" / "optimal" / "practical" justified.',
  'data-auditor': 'Data auditor: an accountant. Recomputes every ratio, sum, phase total, proof-size component and ' +
    'soundness term in every table from EVIDENCE.md rows and logs.',
  'desk-reject': 'Desk-reject auditor: a PC chair. Page limit, template, fonts, page numbers, anonymity (run ' +
    'skills/anonymize-check, incl. repository and package-manifest identities), every URL resolves, references complete.',
}
// The persona that is mandatory for each paper type comes first; 3 core personas by default, plus the optional ones.
const CORE_ORDER = {
  protocol: ['soundness', 'implementation', 'application'],
  system: ['implementation', 'soundness', 'application'],
  application: ['application', 'soundness', 'implementation'],
}

function selectPersonas(paperType, extra) {
  const core = CORE_ORDER[paperType] || CORE_ORDER.protocol
  const opt = (extra || []).filter(x => x === 'data-auditor' || x === 'desk-reject')
  return core.concat(opt.filter((x, i) => opt.indexOf(x) === i)).slice(0, 5)
}

// Meta-review routing: finding category -> agent that owns the fix (the falsifier re-checks soundness and circuits).
const ROUTES = {
  soundness: 'theorist', 'fiat-shamir': 'theorist', theory: 'theorist', circuits: 'circuit-engineer',
  implementation: 'prover-engineer', benchmark: 'experimenter', baseline: 'baseline-engineer', data: 'experimenter',
  writing: 'writer', figures: 'figure-artist', citations: 'lit-scout', novelty: 'lit-scout',
  anonymity: 'submission-rebuttal', layout: 'submission-rebuttal', compliance: 'submission-rebuttal',
}
const RECHECK_BY_FALSIFIER = ['soundness', 'fiat-shamir', 'circuits']

function route(category) {
  const owner = ROUTES[category] || 'writer'
  return { owner, recheck: RECHECK_BY_FALSIFIER.includes(category) ? 'falsifier' : null }
}
// END PURE

const ptype = args.paper_type || 'protocol'
const chosen = selectPersonas(ptype, args.extra)
const FINDING = { type: 'object', properties: {
  id: { type: 'string' }, category: { type: 'string', enum: Object.keys(ROUTES) },
  severity: { type: 'string', enum: ['high', 'med', 'low'] }, location: { type: 'string' },
  finding: { type: 'string' }, suggested_fix: { type: 'string' } }, required: ['id', 'category', 'severity', 'location', 'finding'] }
const REVIEW = { type: 'object', properties: { score: { type: 'number', description: 'six-point scale' },
  confidence: { type: 'number', description: '1-4' }, dimensions: { type: 'object' },
  strengths: { type: 'array', items: { type: 'string' } }, weaknesses: { type: 'array', items: FINDING },
  questions: { type: 'array', items: { type: 'string' } } }, required: ['score', 'confidence', 'weaknesses'] }
const CHECK = { type: 'object', properties: { status: { type: 'string', enum: ['confirmed', 'false-positive', 'unverifiable'] },
  evidence: { type: 'string', description: 'script / log / recomputed cell that settles it' } }, required: ['status', 'evidence'] }

phase('Brief')
await agent(`Write ${P}/reviews/REVIEW-BRIEF.md per skills/mock-review step 1: venue ${V}, paper ${P}/${PDF} and its sha256, ` +
  `the falsifiable statement list (from CLAIMS.md and the contribution list), persona assignments ${JSON.stringify(chosen)} ` +
  `(paper type: ${ptype}), and what is out of scope.`, { agentType: 'reviewer-sim', label: 'brief', effort: 'low' })

phase('Review')
const reviews = await pipeline(chosen,
  key => agent(`Review ${P}/${PDF} for ${V} as this persona — ${PERSONAS[key]} Read ${P}/reviews/REVIEW-BRIEF.md and try to ` +
    `REFUTE its statements first. Use skills/venue-calibration for the scale. Check claims against ${P}/CLAIMS.md, numbers ` +
    `against ${P}/EVIDENCE.md. Every weakness cites a page/section/equation and proposes a fix. Read-only: never edit the paper.`,
    { agentType: 'reviewer-sim', phase: 'Review', label: key, schema: REVIEW }),
  // Verify each finding as soon as its review is in (skills/mock-review step 3)
  (rev, key) => rev && parallel((rev.weaknesses || []).map(w => () =>
    agent(`Verify this mock-review finding against the source, data or a script (reproduce the counterexample, open the log, ` +
      `recompute the cell); write any script under ${P}/reviews/verify/. Finding (${key}): ${JSON.stringify(w)}`,
      { phase: 'Verify', label: `verify:${key}:${w.id}`, schema: CHECK, effort: 'low' })
      .then(c => ({ ...w, persona: key, check: c || { status: 'unverifiable', evidence: 'verifier failed' } }))))
    .then(ws => ({ persona: key, ...rev, weaknesses: ws.filter(Boolean) })))
const done = reviews.filter(Boolean)
const missing = chosen.filter(k => !done.some(r => r.persona === k))
if (missing.length) log(`WARNING: no review from ${missing.join(', ')}; the meta-review says so`)

phase('Meta')
const items = done.flatMap(r => r.weaknesses.filter(w => w.check.status === 'confirmed')
  .map(w => ({ ...w, ...route(w.category) })))
log(`${items.length} confirmed findings routed to agents`)
return await agent(`Write round k of ${P}/REVIEWS.md in the output format of skills/mock-review (score table, per-persona ` +
  `reviews, meta-review as a simulated discussion, verified-findings table; personas are views of one analysis, not ` +
  `independent experts; missing personas: ${JSON.stringify(missing)}). Then write ${P}/reviews/SUBMIT-FIXES.md: confirmed ` +
  `findings graded must-fix / should-fix / won't-fix (with reason), each with its owner agent and, where given, the ` +
  `falsifier re-check; include "good news" items and the 3-6 likeliest rebuttal questions.\n` +
  `Reviews: ${JSON.stringify(done)}\nRouted confirmed findings: ${JSON.stringify(items)}`,
  { agentType: 'reviewer-sim', label: 'meta-review' })

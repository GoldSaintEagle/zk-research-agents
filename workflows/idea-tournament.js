export const meta = {
  name: 'cra-idea-tournament',
  description: 'Generate ZK ideas along 5 design axes, cost-model them with constraint-cost / prover-cost-model at equal soundness, pre-emption check, one judge ranks survivors on 3 criteria',
  whenToUse: 'Phase P2 ideation',
  phases: [{ title: 'Generate' }, { title: 'Screen' }, { title: 'Judge' }],
}
// args: { project: "/abs/path", problem: "the bottleneck / open problem" }

// ---- pure functions (workflows/tests/ loads the block between the markers) ----
// BEGIN PURE
// Borda count over per-criterion rankings (best-first name lists). Unknown names are ignored; ties keep the
// input order (stable sort), so with no rankings the screening order is kept.
function bordaOrder(names, rankings) {
  const n = names.length, score = Object.create(null)
  names.forEach(x => { score[x] = 0 })
  ;(rankings || []).forEach(r => (r || []).forEach((x, i) => { if (x in score) score[x] += n - i }))
  return names.slice().sort((a, b) => score[b] - score[a])
}
// END PURE
const P = (args && args.project) || '.', Q = (args && args.problem) || 'the bottleneck named in STATE.md'
const IDEAS = { type: 'object', properties: { ideas: { type: 'array', items: { type: 'object', properties: {
  name: { type: 'string' }, mechanism: { type: 'string' }, expected_gain: { type: 'string' }, kill_criterion: { type: 'string' } },
  required: ['name', 'mechanism', 'kill_criterion'] } } }, required: ['ideas'] }
// The five axes follow the "ZK design axes" table of skills/idea-mining-loop (Gate A: name the parameter fixed by habit).
const ANGLES = [
  'low-degree test and PCS: free a parameter prior work fixed (FRI folding factor, code rate, query count; KZG vs IPA vs FRI/STIR/WHIR vs a multilinear PCS) and sweep it at fixed soundness bits and regime',
  'field choice: Goldilocks vs BabyBear/KoalaBear vs Mersenne31 vs binary tower fields — native word size of the statement, extension-field challenges, 2-adicity and NTT limits',
  'arithmetization shape: gate degree vs number of columns, custom gates and quotient blow-up, sum-check (multilinear) vs univariate quotient provers',
  'lookup vs native constraints: range checks, bit decomposition and non-native arithmetic via lookups (table size, multiplicity columns, amortisation) vs plain constraints',
  'recursion vs folding: where the boundary between folding steps and the final SNARK / wrapper sits, verifier-circuit size, in-circuit hash choice',
]
phase('Generate')
const ideas = (await parallel(ANGLES.map((a, i) => () => agent(
  `Problem: ${Q}. Read ${P}/LITERATURE.md and ${P}/IDEAS.md. Design axis: ${a}. Follow steps 0-3 of skills/idea-mining-loop (probe target, cheap probe, fixed-by-habit parameter). Propose up to 3 concrete ideas, each with a kill criterion.`,
  { agentType: 'idea-miner', phase: 'Generate', label: `angle${i + 1}`, schema: IDEAS })))).filter(Boolean).flatMap(r => r.ideas)
log(`${ideas.length} raw ideas`)
phase('Screen')
const SCREEN = { type: 'object', properties: { alive: { type: 'boolean' },
  cost_tool: { type: 'string', enum: ['constraint-cost', 'prover-cost-model', 'both'] }, cost_model_gain: { type: 'string' },
  soundness_bits: { type: 'string' }, preempted_by: { type: 'string' }, reason: { type: 'string' } }, required: ['alive', 'cost_tool', 'reason'] }
const screened = await pipeline(ideas,
  idea => agent(`Cost-model this idea on toy parameters before anything is implemented: circuit-side ideas with ` +
    `skills/constraint-cost (constraints / rows / columns / degree / lookups, scripts/constraint_count.py), prover-side ideas ` +
    `with skills/prover-cost-model (MSM, NTT, hashing, sum-check, proof size; lib/cryptomath/costmodel zkops), both if it ` +
    `touches both. Compare against the baseline at the SAME soundness bits and regime (skills/soundness-budget). Then search ` +
    `for pre-emption with skills/eprint-search including its grey-literature pass. Kill it if the predicted end-to-end gain ` +
    `is < 1.2x, if the gain is bought with a worse soundness regime or a larger proof / verifier cost that is not stated, ` +
    `or if it is already published. Idea: ${JSON.stringify(idea)}`,
    { agentType: 'falsifier', phase: 'Screen', label: `screen:${idea.name}`, schema: SCREEN }).then(s => ({ ...idea, ...s })))
const alive = screened.filter(Boolean).filter(s => s.alive)
log(`${alive.length}/${ideas.length} survived screening`)
if (!alive.length) return { alive: [], note: 'nothing survived; broaden problem or revisit literature' }
phase('Judge')
// One judge ranks on all three criteria in a single call; the Borda count below (pure, tested) combines them.
const CRITERIA = { novelty: 'novelty for a top ZK venue (IACR conferences, CCS, S&P, USENIX Security), counting grey literature as prior art',
  feasibility: 'feasibility within 8 weeks with our prover / circuit stack',
  gain: 'size of the end-to-end gain (prover time, verifier time, proof size) at equal soundness' }
const rankArr = { type: 'array', items: { type: 'string' } }
const RANK = { type: 'object', properties: { novelty: rankArr, feasibility: rankArr, gain: rankArr, rationale: { type: 'string', description: '<= 10 lines' } },
  required: ['novelty', 'feasibility', 'gain'] }
const judged = await agent(`Rank these ideas separately on each of three criteria; for each criterion return all names ` +
  `best-first, judging that criterion alone. ${Object.entries(CRITERIA).map(([k, c]) => `${k}: ${c}.`).join(' ')}\n${JSON.stringify(alive)}`,
  { phase: 'Judge', label: 'judge', schema: RANK })
if (!judged) log('WARNING: judge failed; ideas kept in screening order')
const order = bordaOrder(alive.map(a => a.name), judged ? Object.keys(CRITERIA).map(k => judged[k] || []) : [])
await agent(`Append these ideas to ${P}/IDEAS.md in its template format, ordered: ${order.join(', ')}. Data:\n${JSON.stringify(alive)}`, { label: 'write-ideas', model: 'sonnet', effort: 'low' })
return { order, alive, rationale: judged && judged.rationale }

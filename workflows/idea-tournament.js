export const meta = {
  name: 'cra-idea-tournament',
  description: 'Generate ZK ideas along 5 design axes, cost-model them with constraint-cost / prover-cost-model at equal soundness, pre-emption check, judge panel ranks survivors',
  whenToUse: 'Phase P2 ideation',
  phases: [{ title: 'Generate' }, { title: 'Screen' }, { title: 'Judge' }],
}
// args: { project: "/abs/path", problem: "the bottleneck / open problem" }
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
const RANK = { type: 'object', properties: { ranking: { type: 'array', items: { type: 'string' } }, rationale: { type: 'string' } }, required: ['ranking'] }
const ranks = (await parallel(['novelty for a top ZK venue (IACR conferences, CCS, S&P, USENIX Security), counting grey literature as prior art', 'feasibility within 8 weeks with our prover / circuit stack', 'size of the end-to-end gain (prover time, verifier time, proof size) at equal soundness'].map(c => () =>
  agent(`Rank these ideas by ${c}. Return names best-first.\n${JSON.stringify(alive)}`, { phase: 'Judge', label: c, schema: RANK })))).filter(Boolean)
const score = {}
ranks.forEach(r => r.ranking.forEach((n, i) => { score[n] = (score[n] || 0) + (alive.length - i) }))
const order = alive.map(a => a.name).sort((a, b) => (score[b] || 0) - (score[a] || 0))
await agent(`Append these ideas to ${P}/IDEAS.md in its template format, ordered: ${order.join(', ')}. Data:\n${JSON.stringify(alive)}`, { label: 'write-ideas', effort: 'low' })
return { order, alive }

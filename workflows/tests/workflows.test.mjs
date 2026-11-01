// Run: node --test workflows/tests/        (Node >= 18, no dependencies)
import test from 'node:test'
import assert from 'node:assert/strict'
import { loadPure, runWorkflow, source } from './harness.mjs'

const V = (verdict, extra = {}) => ({ verdict, evidence: `toy evidence for ${verdict}`, ...extra })

// ---------------------------------------------------------------- falsify-round: pure tally ----
const F = loadPure('falsify-round.js', ['tally', 'pickWording', 'lensesFor', 'isCircuitClaim', 'LENSES', 'CIRCUIT_LENS'])
const K3 = ['definitions-model', 'fs-soundness-budget', 'fairness-precedent']
const K4 = K3.concat(['circuit-audit'])

test('tally: every agent failed -> open with an error (was: survived)', () => {
  const t = F.tally([null, null, null], K3)
  assert.equal(t.status, 'open')
  assert.ok(t.errors.some(e => e.includes('no valid votes')))
})

test('tally: malformed verdicts do not count as votes', () => {
  assert.equal(F.tally([{ verdict: 'maybe' }, {}, null], K3).status, 'open')
})

test('tally: one refuted vote -> weakened, with that vote\'s wording', () => {
  const t = F.tally([V('survived'), V('refuted', { weakened_wording: 'holds for k <= 20 only', script_or_log: 'falsify/C1/k.py' }), V('survived')], K3)
  assert.equal(t.status, 'weakened')
  assert.equal(t.weakened_wording, 'holds for k <= 20 only')
  assert.equal(t.wording_from, 'fs-soundness-budget')
})

test('tally: two refuted votes -> refuted', () => {
  assert.equal(F.tally([V('refuted'), V('refuted'), V('survived')], K3).status, 'refuted')
})

test('tally: three survived -> survived', () => {
  const t = F.tally([V('survived'), V('survived'), V('survived')], K3)
  assert.equal(t.status, 'survived')
  assert.deepEqual(t.errors, [])
})

test('tally: a single valid survived vote is not enough -> open', () => {
  const t = F.tally([V('survived'), null, null], K3)
  assert.equal(t.status, 'open')
  assert.ok(t.errors.some(e => e.includes('at least 2')))
})

test('tally: two valid survived votes out of three -> survived, failure reported', () => {
  const t = F.tally([V('survived'), null, V('survived')], K3)
  assert.equal(t.status, 'survived')
  assert.ok(t.errors[0].includes('1/3'))
})

test('tally: weakened without any wording -> open', () => {
  assert.equal(F.tally([V('weakened'), V('survived'), V('survived')], K3).status, 'open')
})

test('tally: circuit claim needs a valid circuit-audit vote to survive', () => {
  assert.equal(F.tally([V('survived'), V('survived'), V('survived'), null], K4).status, 'open')
  assert.equal(F.tally([V('survived'), V('survived'), null, V('survived')], K4).status, 'survived')
})

test('pickWording: script/log first, then refuted over weakened, then longer evidence, then lens order', () => {
  const a = V('weakened', { weakened_wording: 'A', evidence: 'a much longer piece of evidence text' })
  const b = V('weakened', { weakened_wording: 'B', script_or_log: 'falsify/C1/b.log' })
  const c = V('refuted', { weakened_wording: 'C' })
  assert.equal(F.pickWording([a, b, c]).wording, 'B')
  assert.equal(F.pickWording([a, c]).wording, 'C')
  const d = V('weakened', { weakened_wording: 'D', evidence: 'short' })
  assert.equal(F.pickWording([d, a]).wording, 'A')
  assert.equal(F.pickWording([V('weakened', { weakened_wording: 'E' }), V('weakened', { weakened_wording: 'F' })]).wording, 'E')
})

test('lenses: three ZK lenses; circuit claims get a fourth circuit-audit lens', () => {
  assert.deepEqual(F.LENSES.map(l => l.key), K3)
  assert.ok(F.LENSES[0].text.includes('zk-definitions'))
  assert.ok(F.LENSES[1].text.includes('fiat-shamir-audit') && F.LENSES[1].text.includes('soundness-budget'))
  assert.ok(F.LENSES[2].text.includes('baseline-pin') && F.LENSES[2].text.includes('eprint-search'))
  assert.ok(F.CIRCUIT_LENS.text.includes('circuit-audit'))
  assert.deepEqual(F.lensesFor({ text: 'the range-check gadget has a unique witness' }).map(l => l.key), K4)
  assert.deepEqual(F.lensesFor({ text: 'the prover is 2x faster', circuit: true }).map(l => l.key), K4)
  assert.deepEqual(F.lensesFor({ text: '[circuit] Merkle path verification' }).map(l => l.key), K4)
  assert.deepEqual(F.lensesFor({ text: 'knowledge soundness error <= 2^-100' }).map(l => l.key), K3)
})

// ------------------------------------------------------- falsify-round: whole script, mocked ----
function falsifyResponder(claims, votesById) {
  return (prompt, opts) => {
    if (!opts.label) return { claims }
    if (opts.label === 'write-ledger') return 'ok'
    const [id, lens] = opts.label.split(':')
    const v = votesById[id]
    return typeof v === 'function' ? v(lens) : v
  }
}

test('falsify-round end to end: the five required cases', async () => {
  const claims = [
    { id: 'C1', text: 'all agents fail' },
    { id: 'C2', text: 'one refutes' },
    { id: 'C3', text: 'two refute' },
    { id: 'C4', text: 'all survive' },
    { id: 'C5', text: 'the range-check circuit has a unique witness' },
  ]
  const votes = {
    C1: null,
    C2: lens => lens === 'fairness-precedent' ? V('refuted', { weakened_wording: 'C2 holds against v0.6.0 only' }) : V('survived'),
    C3: lens => lens === 'definitions-model' ? V('survived') : V('refuted'),
    C4: V('survived'),
    C5: V('survived'),
  }
  const { result, calls, logs, phases, meta } = await runWorkflow('falsify-round.js', { project: '/tmp/toy' }, falsifyResponder(claims, votes))
  const st = Object.fromEntries(result.claims.map(c => [c.id, c.status]))
  assert.deepEqual(st, { C1: 'open', C2: 'weakened', C3: 'refuted', C4: 'survived', C5: 'survived' })
  assert.equal(result.claims.find(c => c.id === 'C2').weakened_wording, 'C2 holds against v0.6.0 only')
  assert.deepEqual(result.errors.map(e => e.id), ['C1'])
  assert.ok(logs.some(l => l.startsWith('ERROR:')))
  const lensCalls = id => calls.filter(c => (c.opts.label || '').startsWith(id + ':')).map(c => c.opts.label.split(':')[1])
  assert.deepEqual(lensCalls('C4'), K3)
  assert.deepEqual(lensCalls('C5'), K4)
  assert.ok(calls.every(c => !c.opts.label || c.opts.label === 'write-ledger' || c.opts.agentType === 'falsifier'))
  assert.deepEqual(phases, meta.phases.map(p => p.title))
  const ledger = calls.find(c => c.opts.label === 'write-ledger').prompt
  assert.ok(ledger.includes('"status": "open"') && ledger.includes('no valid votes'))
  // contrast for the report: the rule before this change
  const old = vs => { const v = vs.filter(Boolean); const r = v.filter(x => x.verdict === 'refuted').length
    const w = v.filter(x => x.verdict === 'weakened').length; return r >= 2 ? 'refuted' : (r + w >= 1 ? 'weakened' : 'survived') }
  console.log(`  old rule on C1 (all agents failed): ${old([null, null, null])}; new rule: ${st.C1}`)
})

test('falsify-round: agents that throw count as failed votes', async () => {
  const claims = [{ id: 'C9', text: 'x' }]
  const respond = (p, o) => {
    if (!o.label) return { claims }
    if (o.label === 'write-ledger') return 'ok'
    if (o.label.endsWith('fairness-precedent')) return V('survived')
    throw new Error('terminal API error')
  }
  const { result } = await runWorkflow('falsify-round.js', { project: '/tmp/toy' }, respond)
  assert.equal(result.claims[0].status, 'open')
  assert.ok(result.errors[0].errors.some(e => e.includes('2/3')))
})

// -------------------------------------------------------------- other workflows, smoke runs ----
const FORBIDDEN = /tfhe|ckks|bgv|\bfhe\b|s-box|sbox|lattice-estimator|core-svp|\bpsi\b|ToSC|\bFSE\b/i

test('no FHE / lattice / symmetric wording in any workflow script', () => {
  for (const f of ['falsify-round.js', 'idea-tournament.js', 'lit-sweep.js', 'mock-review-panel.js'])
    assert.ok(!FORBIDDEN.test(source(f)), f)
})

test('idea-tournament runs under mocks: 5 ZK axes, constraint-cost / prover-cost-model screening', async () => {
  const respond = (p, o) => {
    if (o.label.startsWith('angle')) return { ideas: [{ name: `idea-${o.label}`, mechanism: 'toy', kill_criterion: 'gain < 1.2x' }] }
    if (o.label.startsWith('screen:')) return { alive: !o.label.endsWith('angle5'), cost_tool: 'both', reason: 'toy' }
    if (o.label === 'write-ideas') return 'ok'
    return { ranking: ['idea-angle2', 'idea-angle1', 'idea-angle3', 'idea-angle4'] }
  }
  const { result, calls } = await runWorkflow('idea-tournament.js', { project: '/tmp/toy', problem: 'toy bottleneck' }, respond)
  assert.equal(calls.filter(c => c.opts.label.startsWith('angle')).length, 5)
  const axes = calls.filter(c => c.opts.label.startsWith('angle')).map(c => c.prompt).join('\n')
  for (const k of ['FRI', 'field', 'gate degree', 'lookup', 'folding']) assert.ok(axes.includes(k), k)
  const screen = calls.find(c => c.opts.label.startsWith('screen:')).prompt
  assert.ok(screen.includes('constraint-cost') && screen.includes('prover-cost-model') && screen.includes('soundness'))
  assert.equal(result.order[0], 'idea-angle2')
  assert.equal(result.alive.length, 4)
})

test('lit-sweep runs under mocks: grey literature mode, no ToSC/FSE', async () => {
  const respond = (p, o) => {
    if (o.label.startsWith('mode')) return { works: [{ id: `2026/${o.label.slice(4)}`, title: 'Toy', relevance: 'toy' }, { id: '2026/1', title: 'Toy', relevance: 'dup' }] }
    if (o.label.startsWith('verify:')) return { exists: o.label !== 'verify:2026/3' }
    return 'synthesized'
  }
  const { result, calls, logs } = await runWorkflow('lit-sweep.js', { project: '/tmp/toy', topic: 'toy lookups' }, respond)
  const modes = calls.filter(c => c.opts.label.startsWith('mode')).map(c => c.prompt).join('\n')
  assert.ok(/grey literature/i.test(modes) && modes.includes('HackMD') && modes.includes('ethresear.ch'))
  assert.equal(calls.filter(c => c.opts.label.startsWith('mode')).length, 5)
  assert.ok(logs.some(l => l.includes('4/5 verified')), logs.join('|'))
  assert.equal(result, 'synthesized')
})

test('mock-review-panel: persona selection and routing (pure)', () => {
  const M = loadPure('mock-review-panel.js', ['selectPersonas', 'route', 'PERSONAS'])
  assert.deepEqual(M.selectPersonas('protocol'), ['soundness', 'implementation', 'application'])
  assert.equal(M.selectPersonas('system')[0], 'implementation')
  assert.equal(M.selectPersonas('application')[0], 'application')
  assert.deepEqual(M.selectPersonas('system', ['desk-reject', 'bogus', 'desk-reject']).slice(3), ['desk-reject'])
  assert.equal(M.selectPersonas('protocol', ['data-auditor', 'desk-reject']).length, 5)
  assert.deepEqual(M.route('soundness'), { owner: 'theorist', recheck: 'falsifier' })
  assert.deepEqual(M.route('circuits'), { owner: 'circuit-engineer', recheck: 'falsifier' })
  assert.deepEqual(M.route('benchmark'), { owner: 'experimenter', recheck: null })
  assert.ok(M.PERSONAS.soundness.includes('soundness-budget') && M.PERSONAS.soundness.includes('Frequent catches'))
})

test('mock-review-panel runs under mocks: verify step filters findings before routing', async () => {
  const respond = (p, o) => {
    if (o.label === 'brief') return 'ok'
    if (o.label.startsWith('verify:')) return { status: o.label.endsWith(':W2') ? 'false-positive' : 'confirmed', evidence: 'toy' }
    if (o.label === 'meta-review') return p
    return { score: 3, confidence: 3, weaknesses: [
      { id: 'W1', category: o.label === 'soundness' ? 'fiat-shamir' : 'benchmark', severity: 'high', location: 'p.3', finding: 'toy' },
      { id: 'W2', category: 'writing', severity: 'low', location: 'p.1', finding: 'toy' }] }
  }
  const { result, calls } = await runWorkflow('mock-review-panel.js',
    { project: '/tmp/toy', venue: 'TOYCRYPT', paper_type: 'system', extra: ['desk-reject'] }, respond)
  assert.deepEqual(calls.filter(c => c.opts.phase === 'Review').map(c => c.opts.label), ['implementation', 'soundness', 'application', 'desk-reject'])
  assert.equal(calls.filter(c => c.opts.phase === 'Verify').length, 8)
  const routed = JSON.parse(result.split('Routed confirmed findings: ')[1])
  assert.equal(routed.length, 4)
  assert.ok(routed.some(r => r.owner === 'theorist' && r.recheck === 'falsifier'))
  assert.ok(routed.every(r => r.check.status === 'confirmed'))
})

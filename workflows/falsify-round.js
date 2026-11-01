export const meta = {
  name: 'cra-falsify-round',
  description: 'Attack every open claim in CLAIMS.md from 3 lenses (4 for circuit claims); a pure tally decides, never survived without 2 valid votes',
  whenToUse: 'Phase P6 gate, or whenever CLAIMS.md has open claims',
  phases: [{ title: 'Load' }, { title: 'Attack' }, { title: 'Ledger' }],
}
// args: { project: "/abs/path/to/research-project" }
const P = (args && args.project) || '.'

// ---- pure functions (no agent calls; workflows/tests/run-tests.mjs loads the block between the markers) ----
// BEGIN PURE
const VERDICTS = ['survived', 'weakened', 'refuted']

const LENSES = [
  { key: 'definitions-model',
    text: 'definitions and model (skills/zk-definitions): is the notion that is claimed the one that is proven ' +
      '(soundness vs knowledge soundness, HVZK vs ZK, adaptive vs non-adaptive), are the model, setup and every ' +
      'assumption in the THEORY.md assumption ledger, is the statement well-posed with explicit quantifiers?' },
  { key: 'fs-soundness-budget',
    text: 'Fiat–Shamir and soundness budget (skills/fiat-shamir-audit, skills/soundness-budget): is everything ' +
      'absorbed before its challenge (statement, public inputs, every commitment), is the multi-round loss accounted ' +
      'for; RECOMPUTE the soundness budget yourself from the parameters (do not re-check the theorist\'s table), keep ' +
      'proven and conjectured terms apart, and try the toy cheating provers of lib/cryptomath/zk on small fields' },
  { key: 'fairness-precedent',
    text: 'fairness and precedent (skills/baseline-pin, skills/eprint-search incl. its grey-literature pass): is the ' +
      'strongest baseline used at a pinned SHA, at the same soundness bits / regime / level definition, same statement, ' +
      'same timing scope and threads, every timed proof verified; is the claim already published on ePrint, in project ' +
      'docs, HackMD, ethresear.ch, vendor blogs or audit reports?' },
]
const CIRCUIT_LENS = {
  key: 'circuit-audit',
  text: 'circuit audit (skills/circuit-audit), re-run independently (the circuit-engineer\'s self-audit does not count): ' +
    'under- and over-constraint, witness uniqueness by exhaustive search on a small field, field wrap-around in range ' +
    'checks, differential tests of the witness generator; counts must come from compiler output',
}
const CIRCUIT_RE = /\[circuit\]|\bcircuits?\b|\bconstraints?\b|under-?constrain|over-?constrain|\bgadgets?\b|\bR1CS\b|\bPlonkish\b|\bAIR\b|range[- ]check|witness[- ]uniqueness/i

function isCircuitClaim(claim) {
  return claim.circuit === true || CIRCUIT_RE.test(claim.text || '')
}

function lensesFor(claim) {
  return isCircuitClaim(claim) ? LENSES.concat([CIRCUIT_LENS]) : LENSES.slice()
}

// Which weakened wording is adopted when several attackers propose one: the vote whose evidence is most
// specific, ranked by (1) it names a script or log that reproduces the attack, (2) refuted before weakened
// (the stronger attack bounds what can still be claimed), (3) longer evidence text, (4) lens order.
function pickWording(votes) {
  const cands = votes
    .map((v, i) => ({ v, i }))
    .filter(x => x.v.verdict !== 'survived' && (x.v.weakened_wording || '').trim())
  cands.sort((a, b) =>
    (Number(!!(b.v.script_or_log || '').trim()) - Number(!!(a.v.script_or_log || '').trim())) ||
    (Number(b.v.verdict === 'refuted') - Number(a.v.verdict === 'refuted')) ||
    ((b.v.evidence || '').length - (a.v.evidence || '').length) ||
    (a.i - b.i))
  return cands.length ? { wording: cands[0].v.weakened_wording.trim(), lens: cands[0].v.lens || null } : null
}

// votes: one entry per lens, null where the agent failed. lensKeys: the lenses that were asked, same order.
function tally(votes, lensKeys) {
  const keys = lensKeys || []
  const valid = []
  votes.forEach((v, i) => {
    if (v && VERDICTS.includes(v.verdict)) valid.push(Object.assign({ lens: keys[i] || null }, v))
  })
  const failed = votes.length - valid.length
  const errors = []
  if (failed) errors.push(`${failed}/${votes.length} falsifier agents returned no valid verdict`)
  if (!valid.length) {
    errors.push('no valid votes: claim stays open (re-run this round)')
    return { status: 'open', votes: valid, weakened_wording: null, wording_from: null, errors }
  }
  const refuted = valid.filter(v => v.verdict === 'refuted').length
  const weakened = valid.filter(v => v.verdict === 'weakened').length
  if (refuted >= 2) return { status: 'refuted', votes: valid, weakened_wording: null, wording_from: null, errors }
  if (refuted + weakened >= 1) {
    const pick = pickWording(valid)
    if (!pick) {
      errors.push('weakened/refuted vote without a defensible weaker wording: claim stays open')
      return { status: 'open', votes: valid, weakened_wording: null, wording_from: null, errors }
    }
    return { status: 'weakened', votes: valid, weakened_wording: pick.wording, wording_from: pick.lens, errors }
  }
  // every valid vote says survived
  if (valid.length < 2) {
    errors.push(`only ${valid.length} valid vote: survived needs at least 2, claim stays open`)
    return { status: 'open', votes: valid, weakened_wording: null, wording_from: null, errors }
  }
  if (keys.includes('circuit-audit') && !valid.some(v => v.lens === 'circuit-audit')) {
    errors.push('circuit claim without a valid circuit-audit vote: claim stays open')
    return { status: 'open', votes: valid, weakened_wording: null, wording_from: null, errors }
  }
  return { status: 'survived', votes: valid, weakened_wording: null, wording_from: null, errors }
}
// END PURE

const CLAIMS = { type: 'object', properties: { claims: { type: 'array', items: { type: 'object',
  properties: { id: { type: 'string' }, text: { type: 'string' },
    circuit: { type: 'boolean', description: 'true if the row is tagged [circuit] or the claim is about a circuit, its constraints or witness' } },
  required: ['id', 'text'] } } }, required: ['claims'] }
const VERDICT = { type: 'object', properties: {
  verdict: { type: 'string', enum: VERDICTS },
  weakened_wording: { type: 'string', description: 'required unless survived: the weaker statement you CAN defend' },
  evidence: { type: 'string' }, script_or_log: { type: 'string' } },
  required: ['verdict', 'evidence'] }

phase('Load')
const { claims } = await agent(`Read ${P}/CLAIMS.md and return every row whose status is "open".`, { schema: CLAIMS, effort: 'low' })
log(`${claims.length} open claims`)

phase('Attack')
const results = await pipeline(claims, c => {
  const lenses = lensesFor(c)
  return parallel(lenses.map(lens => () =>
    agent(`Project: ${P}. Try hard to REFUTE claim ${c.id}: "${c.text}". Lens: ${lens.text}. ` +
          `Read EVIDENCE.md, THEORY.md and CIRCUITS.md for context. Write any script you run under ${P}/falsify/${c.id}/. ` +
          `If uncertain, answer weakened with a precise weaker wording that you CAN defend.`,
          { agentType: 'falsifier', phase: 'Attack', label: `${c.id}:${lens.key}`, schema: VERDICT })))
    .then(vs => {
      const t = tally(vs, lenses.map(l => l.key))
      t.errors.forEach(e => log(`${c.id}: ${e}`))
      return { id: c.id, text: c.text, lenses: lenses.map(l => l.key), ...t }
    })
})

phase('Ledger')
const done = results.map((r, i) => r || { id: claims[i].id, text: claims[i].text, lenses: [], status: 'open', votes: [],
  weakened_wording: null, wording_from: null, errors: ['attack stage failed: claim stays open (re-run this round)'] })
await agent(`Update ${P}/CLAIMS.md: for each claim below set status and append falsifier evidence (short, with script/log paths). ` +
  `For weakened claims write exactly the given weakened_wording (chosen from the vote with the most specific evidence; ` +
  `list the other proposed wordings in the evidence cell). For status open, keep the row open and note the errors. ` +
  `Do not delete rows.\n${JSON.stringify(done, null, 1)}`,
  { label: 'write-ledger', effort: 'low' })
const errors = done.filter(r => r.errors.length).map(r => ({ id: r.id, errors: r.errors }))
if (errors.length) log(`ERROR: ${errors.length} claim(s) with failed or insufficient votes; see the returned errors`)
return { claims: done.map(r => ({ id: r.id, status: r.status, lenses: r.lenses, weakened_wording: r.weakened_wording })), errors }

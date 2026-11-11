export const meta = {
  name: 'cra-lit-sweep',
  description: 'Multi-modal ZK literature sweep (ePrint, DBLP, citation graph, grey literature, library code) → one batched bib-verify run → related-work matrix',
  whenToUse: 'Phase P1, and before submission as a pre-emption check',
  phases: [{ title: 'Sweep' }, { title: 'Verify' }, { title: 'Synthesize' }],
}
// args: { project: "/abs/path", topic: "short topic description", since: "YYYY-MM" }
const P = args.project, T = args.topic, S = args.since || 'last 24 months'
const HITS = { type: 'object', properties: { works: { type: 'array', items: { type: 'object', properties: {
  id: { type: 'string', description: 'ePrint id / DOI / arXiv id, or the URL for a grey-literature source' },
  url: { type: 'string' }, urldate: { type: 'string', description: 'YYYY-MM-DD access date (grey sources)' },
  archiveurl: { type: 'string', description: 'Wayback snapshot (grey sources)' }, title: { type: 'string' }, venue_year: { type: 'string' },
  relevance: { type: 'string' }, technique: { type: 'string' } }, required: ['id', 'title', 'relevance'] } } }, required: ['works'] }
const MODES = [
  `keyword search on IACR ePrint (use skills/eprint-search) for "${T}" since ${S}`,
  `DBLP venue search: CRYPTO/EUROCRYPT/ASIACRYPT/TCC/PKC/CCS/S&P/USENIX Security/FC for "${T}"`,
  `citation-graph walk: start from the 3 most-cited works on "${T}" and follow forward citations`,
  `grey literature (the grey-literature pass of skills/eprint-search): project docs and repos, HackMD, ethresear.ch, ` +
    `vendor technical blogs, public audit reports on "${T}"; window 24 months for blogs/forums/HackMD, all time for docs ` +
    `and audits; record URL, access date and a Wayback snapshot for every hit`,
  `code-first: find public libraries/zkVMs/artifacts implementing "${T}" (start from references/baselines/MANIFEST.md) and the papers they cite`,
]
phase('Sweep')
const found = (await parallel(MODES.map((m, i) => () =>
  agent(`Topic: ${T}. Mode: ${m}. Return only works you actually saw on a web page this session.`,
    { agentType: 'lit-scout', phase: 'Sweep', label: `mode${i + 1}`, model: 'sonnet', schema: HITS })))).filter(Boolean).flatMap(r => r.works)
// ---- pure functions (workflows/tests/ loads the block between the markers) ----
// BEGIN PURE
// Deduplicate hits by id (case-insensitive), keeping the first record seen.
function dedupe(works) {
  const m = new Map()
  works.filter(w => w && w.id).forEach(w => { if (!m.has(w.id.toLowerCase())) m.set(w.id.toLowerCase(), w) })
  return [...m.values()]
}
// Join the single batch verifier's per-id results back onto the candidates. A candidate the verifier did not
// report on counts as unverified (dropped), never as verified.
function mergeVerified(cands, results) {
  const byId = new Map((results || []).filter(r => r && r.id).map(r => [r.id.toLowerCase(), r]))
  return cands.map(w => {
    const r = byId.get(w.id.toLowerCase())
    return r ? { ...w, ...r, id: w.id } : { ...w, exists: false, why: 'not in the verifier report' }
  })
}
// END PURE
const uniq = dedupe(found)
log(`${found.length} hits, ${uniq.length} unique`)
phase('Verify')
// One agent for all candidates: verify_bib.py is rate-limited and cached, so a single run over one .bib is
// cheaper and politer than one agent (and one script run) per work.
const BATCH = { type: 'object', properties: { results: { type: 'array', items: { type: 'object', properties: {
  id: { type: 'string', description: 'the candidate id exactly as given' }, exists: { type: 'boolean' },
  bibtex: { type: 'string' }, one_line_summary: { type: 'string' }, why: { type: 'string', description: 'status line from the report when not verified' } },
  required: ['id', 'exists'] } }, report: { type: 'string', description: 'path of the verify_bib.py report' } }, required: ['results'] }
const v = uniq.length ? await agent(
  `Verify these ${uniq.length} candidate works in ONE batch (skills/bib-verify). Write a BibTeX entry for every candidate ` +
  `into ${P}/notes/sweep/sweep-candidates.bib (papers: url is the official https://eprint.iacr.org/YYYY/NNNN or the DOI, never a ` +
  `mirror URL; grey sources: @misc with url, urldate and archiveurl). Run skills/bib-verify/scripts/verify_bib.py ` +
  `${P}/notes/sweep/sweep-candidates.bib --json ${P}/notes/sweep/sweep-verify.json ONCE (rate-limited, shared cache, third-party mirror ` +
  `if eprint.iacr.org is unreachable) with stdout to ${P}/notes/sweep/sweep-verify.md; do not fetch eprint.iacr.org pages ` +
  `yourself and do not paste the report into your answer. exists = the report says VERIFIED (incl. mirror) for papers, ` +
  `or URL answers + Wayback snapshot + access date for grey sources. Return one result per candidate id, with the ` +
  `corrected bibtex and a one-line summary for verified ones.\n${JSON.stringify(uniq)}`,
  { agentType: 'lit-scout', phase: 'Verify', label: 'verify-batch', model: 'sonnet', effort: 'low', schema: BATCH }) : null
if (uniq.length && !v) log('ERROR: batch verifier failed; every candidate counts as unverified (re-run the Verify phase)')
const verified = mergeVerified(uniq, v && v.results)
const ok = verified.filter(w => w.exists)
log(`${ok.length}/${uniq.length} verified; unverifiable entries dropped`)
phase('Synthesize')
return await agent(`Project ${P}. Merge these verified works into ${P}/LITERATURE.md (matrix format already in the file) and append bibtex to ${P}/refs.bib (no duplicates). ` +
  `Then write a 10-line "threat assessment": which works pre-empt or weaken our thesis in ${P}/STATE.md (read its thesis section, not the whole file)?\n${JSON.stringify(ok)}`,
  { agentType: 'lit-scout', label: 'synthesize' })

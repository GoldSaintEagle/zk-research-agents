// Tally the falsifier's lens votes with the tested tally() of workflows/falsify-round.js (P6, by hand).
//   node falsify/tally.mjs > falsify/tally.log
import { readFileSync } from 'node:fs'
import { loadPure } from '../../../workflows/tests/harness.mjs'

const F = loadPure('falsify-round.js', ['tally', 'lensesFor'])
const votes = JSON.parse(readFileSync(new URL('./votes.json', import.meta.url), 'utf8'))
for (const [id, c] of Object.entries(votes)) {
  if (id.startsWith('_')) continue
  const keys = F.lensesFor({ text: c.text }).map(l => l.key)
  if (keys.length !== c.votes.length) throw new Error(`${id}: ${c.votes.length} votes for ${keys.length} lenses`)
  const t = F.tally(c.votes, keys)
  console.log(`${id}: ${t.status} (lenses: ${keys.join(', ')}; votes: ${c.votes.map(v => v.verdict).join(', ')})` +
    (t.weakened_wording ? `\n    wording (from ${t.wording_from}): ${t.weakened_wording}` : '') +
    (t.errors.length ? `\n    errors: ${t.errors.join('; ')}` : ''))
}

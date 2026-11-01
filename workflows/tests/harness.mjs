// Test harness for the Workflow-tool scripts in workflows/*.js (no dependencies; Node >= 18).
// A script is plain JavaScript with `export const meta = {...}` and a body that uses agent(), parallel(),
// pipeline(), phase(), log() and args. We strip the export, wrap the body in an async function and pass mocks.
import { readFileSync } from 'node:fs'
import { dirname, join } from 'node:path'
import { fileURLToPath } from 'node:url'

export const WF = join(dirname(fileURLToPath(import.meta.url)), '..')
const AsyncFunction = Object.getPrototypeOf(async function () {}).constructor

export function source(name) {
  return readFileSync(join(WF, name), 'utf8')
}

// The block between `// BEGIN PURE` and `// END PURE`, evaluated on its own; returns the named functions/constants.
export function loadPure(name, names) {
  const src = source(name)
  const a = src.indexOf('// BEGIN PURE'), b = src.indexOf('// END PURE')
  if (a < 0 || b < a) throw new Error(`${name}: no PURE block`)
  return new Function(`${src.slice(a, b)}\nreturn { ${names.join(', ')} }`)()
}

// Workflow API rule: schema root is {type: 'object', properties}, and required ⊆ properties (checked recursively).
export function checkSchema(s, where = 'schema') {
  if (!s || s.type !== 'object' || typeof s.properties !== 'object') throw new Error(`${where}: root must be an object schema`)
  for (const r of s.required || []) if (!(r in s.properties)) throw new Error(`${where}: required '${r}' not in properties`)
  for (const [k, v] of Object.entries(s.properties)) {
    if (v && v.type === 'object' && v.properties) checkSchema(v, `${where}.${k}`)
    if (v && v.type === 'array' && v.items && v.items.type === 'object') checkSchema(v.items, `${where}.${k}[]`)
  }
}

// Run a workflow script. respond(prompt, opts) plays the subagent: return a value, null (agent died), or throw.
export async function runWorkflow(name, args, respond) {
  const src = source(name).replace(/^export const meta\s*=/m, 'const meta =')
  const calls = [], logs = [], phases = []
  const agent = async (prompt, opts = {}) => {
    if (opts.schema) checkSchema(opts.schema, `${name}:${opts.label || 'agent'}`)
    calls.push({ prompt, opts })
    return respond(prompt, opts)
  }
  const parallel = async thunks => Promise.all(thunks.map(t => Promise.resolve().then(t).catch(() => null)))
  const pipeline = async (items, ...stages) => Promise.all(items.map(async (item, i) => {
    let r = item
    for (const s of stages) {
      try { r = await s(r, item, i) } catch { return null }
    }
    return r
  }))
  const fn = new AsyncFunction('agent', 'parallel', 'pipeline', 'phase', 'log', 'args', 'budget', src + '\n')
  const budget = { total: null, spent: () => 0, remaining: () => Infinity }
  const result = await fn(agent, parallel, pipeline, t => phases.push(t), m => logs.push(m), args, budget)
  const meta = new Function(src.match(/const meta =[\s\S]*?\n}\n/)[0] + '\nreturn meta')()
  return { result, calls, logs, phases, meta }
}

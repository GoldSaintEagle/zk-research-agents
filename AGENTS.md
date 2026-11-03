# zk-research-agents — instructions for Codex / generic coding agents

This repo is a **toolkit**, not a research project. Research happens in a separate
project directory initialised with `/cra-init <dir>` (see `docs/QUICKSTART.md`).

When working *in a research project* that uses this system:
1. Read `STATE.md` first. The `pi-orchestrator` agent (agents/pi-orchestrator.md) owns phase changes.
2. Hand work between agents **only through blackboard files** (`templates/blackboard/`).
3. Invariants (never break):
   - A statement enters `paper/` only if its `CLAIMS.md` status is `survived` (or `weakened`, using the weakened wording).
   - A number enters `paper/` only if it has an `EVIDENCE.md` row; run `crbench audit-tex paper/main.tex EVIDENCE.md`.
   - A bib entry stays only if `skills/bib-verify` confirmed it exists.
   - Nothing leaves the machine (submission, e-mail, eprint, public repo) without explicit human approval.
4. Prefer `lib/cryptomath` + `lib/bench` over ad-hoc scripts; put throw-away scripts under `falsify/<claim-id>/` or `results/<exp>/`.
5. Toy implementations in `lib/cryptomath/zk|protocols|ec` (sum-check, Merkle, FRI, KZG algebra, permutation/lookup checks, R1CS/Plonkish) are **insecure** and only for reasoning / small experiments.

When working *on this repo*: follow `SPEC.md` (names, formats, the no-private-content rule).

## Using this toolkit from Codex
Install with `./install.sh <project-dir> --codex` (or `--user --codex`). It runs `scripts/codex_export.py`, which
writes the Codex layout:
- `.agents/skills/<name>/`: the 34 skills, unchanged (Agent Skills format: `SKILL.md` + `scripts/`);
- `.agents/skills/cra-<x>/`: each slash command from `commands/` turned into a skill (Codex custom prompts are
  deprecated), invoked as `$cra-init`, `$cra-phase P3`, ... or by asking for it by name;
- `.codex/agents/<name>.toml`: the 13 agents as Codex custom subagents (`name`, `description`,
  `developer_instructions`), generated from `agents/*.md`; edit the `.md` files and re-install, never the TOML.

Mapping when a file here says something Claude-specific:
- "dispatch <agent>" / "the Agent tool" = spawn the custom subagent `<agent>` (ask Codex to spawn it by name).
  Keep the separation the process relies on: the falsifier's independent re-runs (soundness budget, circuit and
  Fiat–Shamir audits) go to a separate `falsifier` subagent that has not seen the builder's result.
- `skills/<name>/` = `.agents/skills/<name>/`; `workflows/` = `.cra/workflows/`; `templates/` is in the toolkit
  directory named in `.cra/toolkit-path` (written by a project install; with `--user`, ask the user for it).
- `workflows/*.js` need Claude Code's Workflow tool. Under Codex, run the same rounds by spawning the subagents the
  script names, and decide the votes with the pure `tally()` of `workflows/falsify-round.js`, loaded through
  `loadPure` from `workflows/tests/harness.mjs` (see `case-study/toy-rangecheck/falsify/tally.mjs`).

## Using the agents without subagents
Each file in `agents/` is a self-contained role prompt. In tools without subagents,
"become" an agent by reading its file and following its Procedure; skills in
`skills/<name>/SKILL.md` are plain Markdown procedures with optional scripts.
Slash commands in `commands/` are equivalent to typing their body as a prompt.

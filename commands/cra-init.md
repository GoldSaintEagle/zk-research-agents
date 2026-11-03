---
description: Scaffold the research blackboard into a project directory
argument-hint: <project-dir>
---

Copy every file in templates/blackboard/ of the zk-research-agents toolkit into $ARGUMENTS (create it if needed; never overwrite existing files; this includes an empty refs.bib, which lit-scout owns and paper/main.tex reads as ../refs), create subdirs results/ paper/ baselines/ lean/ falsify/ impl/ circuits/ (impl/ is owned by prover-engineer, circuits/ by circuit-engineer), copy templates/paper/ into paper/ if paper/ is empty, then ask the user for the one-sentence thesis, the paper type (protocol / system / application; it decides whether prover-engineer and circuit-engineer are needed), target venue and deadline and fill STATE.md (phase P0).

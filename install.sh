#!/usr/bin/env bash
# Install agents / skills / commands into a target project's .claude/ (or ~/.claude with --user).
# Usage: ./install.sh <target-project-dir> [--link]     # --link = symlink instead of copy
#        ./install.sh --user [--link]
#        ./install.sh <target-project-dir>|--user --codex [--link]   # OpenAI Codex layout instead:
#            .agents/skills/ (skills + commands as skills) and .codex/agents/*.toml (scripts/codex_export.py)
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MODE=copy; TARGET=""; CODEX=0
for a in "$@"; do case "$a" in --link) MODE=link;; --user) TARGET="$HOME";; --codex) CODEX=1;; *) TARGET="$a";; esac; done
[ -n "$TARGET" ] || { echo "usage: $0 <project-dir>|--user [--link] [--codex]"; exit 1; }
if [ "$CODEX" = 1 ]; then
  args=(); [ "$TARGET" = "$HOME" ] && args+=(--user) || args+=(--dest "$TARGET"); [ "$MODE" = link ] && args+=(--link)
  python3 "$HERE/scripts/codex_export.py" "${args[@]}"
  echo "Python libs: pip install -e $HERE/lib/cryptomath -e $HERE/lib/bench"
  echo "Next: in Codex run  \$cra-init  (or ask for it by name)"
  exit 0
fi
DEST="$TARGET/.claude"; mkdir -p "$DEST/agents" "$DEST/skills" "$DEST/commands"
put() { if [ "$MODE" = link ]; then ln -sfn "$1" "$2"; else rm -rf "$2"; cp -r "$1" "$2"; fi; }
for f in "$HERE"/agents/*.md;   do put "$f" "$DEST/agents/$(basename "$f")"; done
for d in "$HERE"/skills/*/;     do put "${d%/}" "$DEST/skills/$(basename "$d")"; done
for f in "$HERE"/commands/*.md; do put "$f" "$DEST/commands/$(basename "$f")"; done
if [ "$TARGET" != "$HOME" ]; then
  mkdir -p "$TARGET/.cra"; put "$HERE/workflows" "$TARGET/.cra/workflows"
  [ -f "$TARGET/AGENTS.md" ] || cp "$HERE/AGENTS.md" "$TARGET/AGENTS.md"
fi
echo "Installed into $DEST ($MODE). Python libs: pip install -e $HERE/lib/cryptomath -e $HERE/lib/bench"
echo "Next: in Claude Code run  /cra-init <project-dir>"

#!/usr/bin/env bash
# Grep the repo against a local deny-list before pushing. Exit 1 on any hit.
# Deny-list: .privacy-denylist (git-ignored), one extended regex per line, '#' comments.
# Lines starting with '!' are allow patterns: a hit line that also matches one of them is dropped
# (for values that are public on purpose, e.g. the fork URL in polite_http.py's User-Agent).
# Scans what git would publish: tracked files plus untracked files that are not git-ignored
# (build output such as *.fls with absolute paths is ignored, so it is not scanned).
set -uo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"; LIST="${1:-$ROOT/.privacy-denylist}"
[ -f "$LIST" ] || { echo "no deny-list at $LIST (create one; it is git-ignored)"; exit 2; }
PAT=$(grep -vE '^[[:space:]]*(#|!|$)' "$LIST" | paste -sd'|' -)   # '-' operand: BSD paste requires it
ALLOW=$(grep -E '^!' "$LIST" | sed 's/^!//' | paste -sd'|' -)
[ -n "$PAT" ] || { echo "deny-list $LIST has no patterns (an empty pattern would match every file)"; exit 2; }
cd "$ROOT" || exit 2
FILES=$(git ls-files -z --cached --others --exclude-standard | tr '\0' '\n' | grep -vx '.privacy-denylist')
HITS=$(printf '%s\n' "$FILES" | while IFS= read -r f; do [ -f "$f" ] && printf '%s\0' "$f"; done \
       | xargs -0 grep -niIE "$PAT" -- 2>/dev/null || true)
[ -n "$ALLOW" ] && [ -n "$HITS" ] && HITS=$(printf '%s\n' "$HITS" | grep -viE "$ALLOW" || true)
# also scan text inside PDFs we ship
while IFS= read -r f; do
  [ -f "$f" ] || continue
  pdftotext -q "$f" - 2>/dev/null | grep -qiE "$PAT" && HITS+=$'\n'"PDF text hit: $f"
  pdfinfo "$f" 2>/dev/null | grep -qiE "$PAT" && HITS+=$'\n'"PDF metadata hit: $f"
done < <(printf '%s\n' "$FILES" | grep -iE '\.pdf$')
HITS=$(printf '%s' "$HITS" | sed '/^$/d')
if [ -n "$HITS" ]; then echo "$HITS"; echo "PRIVACY SCAN FAILED"; exit 1; fi
echo "privacy scan clean ($(printf '%s\n' "$FILES" | wc -l | tr -d ' ') files)"

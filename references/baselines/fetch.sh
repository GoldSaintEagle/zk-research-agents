#!/usr/bin/env bash
# fetch.sh -- clone public baseline libraries at a pinned ref into a directory you choose.
#
# Usage:
#   references/baselines/fetch.sh --list
#   references/baselines/fetch.sh DEST_DIR [NAME ...]          # default: nothing; name what you need
#   references/baselines/fetch.sh DEST_DIR --all
#   references/baselines/fetch.sh DEST_DIR --dry-run plonky3 halo2-pse
#   PIN_halo2_pse=<full-sha-or-tag> references/baselines/fetch.sh DEST_DIR halo2-pse   # override a pin
#   references/baselines/fetch.sh --selftest   # offline: catalogue vs MANIFEST.md vs crbench parsers
#
# Refs: a tag pins a release. HEAD means "no release tag, so pin at fetch time". In both
# cases the resolved commit SHA is appended to DEST_DIR/PINNED.tsv. Copy that SHA into your
# project's baselines/MANIFEST.md. From then on, re-fetch by SHA only.
#
# No source is vendored into this repository (SPEC rule 3). This script only clones.
set -euo pipefail

# name | url | suggested ref | crbench parser ("-" = none yet)
# Refs are release tags seen with `git ls-remote --tags` on 2026-11-01, or HEAD where there was no
# stable release tag. They are starting points: copy the resolved full SHA into your project MANIFEST.
CATALOG='
arkworks-algebra|https://github.com/arkworks-rs/algebra.git|v0.6.0|criterion
arkworks-groth16|https://github.com/arkworks-rs/groth16.git|v0.6.0|criterion
halo2-pse|https://github.com/privacy-scaling-explorations/halo2.git|v2023_04_20|criterion
halo2-zcash|https://github.com/zcash/halo2.git|halo2_proofs-0.4.0|criterion
plonky2|https://github.com/0xPolygonZero/plonky2.git|v1.1.0|criterion
plonky3|https://github.com/Plonky3/Plonky3.git|v0.8.0|criterion
gnark|https://github.com/Consensys/gnark.git|v0.16.4|gobench
lambdaworks|https://github.com/lambdaclass/lambdaworks.git|v0.15.0|criterion
expander|https://github.com/PolyhedraZK/Expander.git|v1.2.0|generic
binius64|https://github.com/binius-zk/binius64.git|HEAD|generic
binius|https://github.com/IrreducibleOSS/binius.git|HEAD|criterion
stwo|https://github.com/starkware-libs/stwo.git|v2.3.0|criterion
icicle|https://github.com/ingonyama-zk/icicle.git|v4.0.0|criterion
circom|https://github.com/iden3/circom.git|v2.2.3|circom
snarkjs|https://github.com/iden3/snarkjs.git|v0.7.6|snarkjs
rapidsnark|https://github.com/iden3/rapidsnark.git|v0.0.8|rapidsnark
noir|https://github.com/noir-lang/noir.git|v1.0.0|nargo-info
barretenberg|https://github.com/AztecProtocol/barretenberg.git|v6.0.0|shell-time
risc0|https://github.com/risc0/risc0.git|v3.0.6|risc0
sp1|https://github.com/succinctlabs/sp1.git|v6.10.0|sp1
jolt|https://github.com/a16z/jolt.git|HEAD|-
nova|https://github.com/microsoft/Nova.git|HEAD|criterion
sonobe|https://github.com/privacy-scaling-explorations/sonobe.git|HEAD|criterion
cadical|https://github.com/arminbiere/cadical.git|rel-3.0.1|sat
kissat|https://github.com/arminbiere/kissat.git|rel-4.0.4|sat
'

list() {
  printf '%-18s %-20s %-12s %s\n' NAME REF PARSER URL
  echo "$CATALOG" | while IFS='|' read -r n u r p; do
    [ -z "$n" ] && continue
    printf '%-18s %-20s %-12s %s\n' "$n" "$r" "$p" "$u"
  done
}

lookup() {  # name -> "url|ref"
  echo "$CATALOG" | awk -F'|' -v n="$1" '$1==n {print $2"|"$3}'
}

pin_var() {  # name -> PIN_<name> with '-' mapped to '_' (halo2-pse -> PIN_halo2_pse)
  echo "PIN_$(echo "$1" | tr '-' '_')"
}

# Offline self-check: catalogue well-formed and in sync with MANIFEST.md and the crbench parser registry.
selftest() {
  local here manifest parsers fail=0 n u r p extra
  here="$(cd "$(dirname "$0")" && pwd)"
  manifest="$here/MANIFEST.md"
  parsers="$here/../../lib/bench/crbench/parsers.py"
  [ -f "$manifest" ] && [ -f "$parsers" ] || { echo "selftest: MANIFEST.md or parsers.py missing" >&2; return 1; }
  dup="$(echo "$CATALOG" | awk -F'|' 'NF{print $1}' | sort | uniq -d)"
  [ -z "$dup" ] || { echo "duplicate names: $dup" >&2; fail=1; }
  while IFS='|' read -r n u r p extra; do
    [ -z "$n" ] && continue
    [ -z "$extra" ] || { echo "$n: too many fields" >&2; fail=1; }
    echo "$n" | grep -Eq '^[a-z0-9][a-z0-9-]*$' || { echo "$n: name not kebab-case" >&2; fail=1; }
    echo "$u" | grep -Eq '^https://github\.com/[^/]+/[^/]+\.git$' || { echo "$n: bad url $u" >&2; fail=1; }
    echo "$r" | grep -Eq '^[A-Za-z0-9._-]+$' || { echo "$n: bad ref '$r'" >&2; fail=1; }
    echo "$r" | grep -Eq '^[0-9a-f]{7,40}$' && { echo "$n: catalogue must not carry SHAs" >&2; fail=1; }
    grep -q "^| \`$n\` | ${u%.git} |" "$manifest" || { echo "$n: no MANIFEST row with url ${u%.git}" >&2; fail=1; }
    grep "^| \`$n\` |" "$manifest" | grep -q "| \`$r\`" || { echo "$n: MANIFEST tag differs from $r" >&2; fail=1; }
    if [ "$p" = "-" ]; then
      grep "^| \`$n\` |" "$manifest" | grep -q "none yet" || { echo "$n: MANIFEST should say 'none yet'" >&2; fail=1; }
    else
      grep -q "register_parser(\"$p\"" "$parsers" || { echo "$n: parser '$p' not registered in crbench" >&2; fail=1; }
      grep "^| \`$n\` |" "$manifest" | grep -q "\`$p\`" || { echo "$n: MANIFEST row does not name parser $p" >&2; fail=1; }
    fi
  done <<< "$CATALOG"
  # every fetch name in MANIFEST.md is in the catalogue
  for n in $(grep -oE '^\| `[a-z0-9-]+` \| https://' "$manifest" | sed -E 's/^\| `([^`]+)`.*/\1/'); do
    [ -n "$(lookup "$n")" ] || { echo "MANIFEST row $n missing from fetch.sh" >&2; fail=1; }
  done
  [ "$(lookup halo2-pse)" = "https://github.com/privacy-scaling-explorations/halo2.git|v2023_04_20" ] || { echo "lookup broken" >&2; fail=1; }
  [ "$(pin_var halo2-pse)" = "PIN_halo2_pse" ] || { echo "pin_var broken" >&2; fail=1; }
  [ -z "$(lookup no-such-lib)" ] || { echo "lookup of unknown name returned something" >&2; fail=1; }
  if [ "$fail" = 0 ]; then echo "fetch.sh selftest: OK ($(echo "$CATALOG" | grep -c '|') baselines)"; fi
  return $fail
}

if [ "${1:-}" = "--list" ] || [ "${1:-}" = "-l" ]; then list; exit 0; fi
if [ "${1:-}" = "--selftest" ]; then selftest; exit $?; fi
if [ $# -lt 1 ] || [ "${1:-}" = "-h" ] || [ "${1:-}" = "--help" ]; then
  sed -n '2,16p' "$0"; exit 0
fi

DEST="$1"; shift
DRY=0; NAMES=()
for a in "$@"; do
  case "$a" in
    --dry-run) DRY=1 ;;
    --all) while IFS='|' read -r n _u _r _p; do [ -n "$n" ] && NAMES+=("$n"); done <<< "$CATALOG" ;;
    *) NAMES+=("$a") ;;
  esac
done
if [ ${#NAMES[@]} -eq 0 ]; then echo "no baselines named; see --list" >&2; exit 2; fi

[ "$DRY" = 1 ] || mkdir -p "$DEST"
PINS="$DEST/PINNED.tsv"
if [ "$DRY" = 0 ] && [ ! -f "$PINS" ]; then printf 'name\turl\trequested_ref\tresolved_commit\tfetched_utc\n' > "$PINS"; fi

rc=0
for n in "${NAMES[@]}"; do
  entry="$(lookup "$n")"
  if [ -z "$entry" ]; then echo "unknown baseline: $n (see --list)" >&2; rc=2; continue; fi
  url="${entry%%|*}"; ref="${entry#*|}"
  var="$(pin_var "$n")"
  ref="${!var:-$ref}"
  dir="$DEST/$n"
  if [ "$DRY" = 1 ]; then
    echo "would clone $url -> $dir at $ref"; continue
  fi
  if [ -d "$dir/.git" ]; then
    echo "[$n] exists, fetching"; git -C "$dir" fetch --tags --quiet origin
  else
    echo "[$n] cloning $url"; git clone --quiet --filter=blob:none "$url" "$dir"
  fi
  if [ "$ref" != "HEAD" ]; then
    git -C "$dir" -c advice.detachedHead=false checkout --quiet "$ref"
  fi
  git -C "$dir" submodule update --init --recursive --quiet || echo "[$n] warning: submodule update failed" >&2
  sha="$(git -C "$dir" rev-parse HEAD)"
  printf '%s\t%s\t%s\t%s\t%s\n' "$n" "$url" "$ref" "$sha" "$(date -u +%Y-%m-%dT%H:%M:%SZ)" >> "$PINS"
  echo "[$n] pinned at $sha"
done
exit $rc

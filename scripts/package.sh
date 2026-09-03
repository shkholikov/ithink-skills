#!/usr/bin/env bash
# Build one uploadable .zip per skill into dist/.
#
#   ./scripts/package.sh                  # all skills
#   ./scripts/package.sh system-diagram   # just one
#
# The zip contains the skill folder as its single top-level entry, which is what
# claude.ai expects. A zip with SKILL.md at its root is rejected.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

ALL_SKILLS=(topology-creator system-diagram ithink-documents)

# Always dropped — build noise that would only bloat the upload.
COMMON_EXCLUDES=('*/__pycache__/*' '*.pyc' '*.DS_Store')

# Per-skill drops. Only strip a folder the skill's own SKILL.md never points at:
# system-diagram documents examples/harness.json, so its examples/ must ship,
# while topology-creator's examples/ is 3.9M of README renders nothing reads.
skill_excludes() {
  case "$1" in
    topology-creator) printf '%s\n' 'topology-creator/examples/*' ;;
    *) ;;
  esac
}

skills=("${@:-}")
if [[ -z "${skills[0]:-}" ]]; then
  skills=("${ALL_SKILLS[@]}")
fi

mkdir -p dist

for skill in "${skills[@]}"; do
  if [[ ! -f "$skill/SKILL.md" ]]; then
    echo "error: $skill/SKILL.md not found — is '$skill' a skill folder?" >&2
    exit 1
  fi

  zipfile="dist/$skill-skill.zip"
  rm -f "$zipfile"

  excludes=()
  for pattern in "${COMMON_EXCLUDES[@]}"; do excludes+=(-x "$pattern"); done
  while IFS= read -r pattern; do
    [[ -n "$pattern" ]] && excludes+=(-x "$pattern")
  done < <(skill_excludes "$skill")

  zip -qr "$zipfile" "$skill" "${excludes[@]}"

  # Guard the classic packaging mistake before anyone uploads it.
  tops=$(unzip -Z1 "$zipfile" | cut -d/ -f1 | sort -u)
  if [[ "$tops" != "$skill" ]]; then
    echo "error: $zipfile has top-level entries '$tops', expected only '$skill'" >&2
    exit 1
  fi
  unzip -Z1 "$zipfile" | grep -qx "$skill/SKILL.md" || {
    echo "error: $zipfile is missing $skill/SKILL.md" >&2
    exit 1
  }

  printf '%-20s %s\n' "$skill" "$(du -h "$zipfile" | cut -f1)"
done

#!/usr/bin/env bash
# Build one uploadable .zip per skill into dist/.
#
#   ./scripts/package.sh                        # all skills, version from git
#   ./scripts/package.sh system-diagram         # just one
#   ./scripts/package.sh --version v1.1.0       # stamp an explicit version
#
# The zip contains the skill folder as its single top-level entry, which is what
# claude.ai expects. A zip with SKILL.md at its root is rejected.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

ALL_SKILLS=(topology-creator system-diagram ithink-documents amocrm-expert)
RELEASES_URL="https://github.com/shkholikov/ithink-skills/releases/latest"

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

version=""
skills=()
while [[ $# -gt 0 ]]; do
  case "$1" in
    --version) version="${2:?--version needs a value}"; shift 2 ;;
    -h|--help) sed -n '2,9p' "$0"; exit 0 ;;
    -*) echo "error: unknown option $1" >&2; exit 1 ;;
    *) skills+=("$1"); shift ;;
  esac
done

if [[ -z "$version" ]]; then
  version="${SKILL_VERSION:-$(git describe --tags --always --dirty 2>/dev/null || echo dev)}"
fi
if [[ ${#skills[@]} -eq 0 ]]; then
  skills=("${ALL_SKILLS[@]}")
fi

stage="$(mktemp -d)"
trap 'rm -rf "$stage"' EXIT

mkdir -p dist

for skill in "${skills[@]}"; do
  if [[ ! -f "$skill/SKILL.md" ]]; then
    echo "error: $skill/SKILL.md not found — is '$skill' a skill folder?" >&2
    exit 1
  fi

  # A per-skill tag (system-diagram-v1.1.0) stamps as plain v1.1.0.
  display_version="${version#"$skill"-}"

  rm -rf "${stage:?}/$skill"
  cp -R "$skill" "$stage/$skill"

  # Stamp the version into the body, not the frontmatter: claude.ai validates
  # frontmatter and only accepts `name` and `description` there. In the body it
  # is a line Claude can read back when someone asks which version they have.
  python3 - "$stage/$skill/SKILL.md" "$display_version" "$RELEASES_URL" <<'PY'
import pathlib, sys

path, version, url = sys.argv[1], sys.argv[2], sys.argv[3]
doc = pathlib.Path(path)
text = doc.read_text(encoding="utf-8")
if not text.startswith("---\n"):
    sys.exit(f"error: {path} has no YAML frontmatter")
end = text.index("\n---\n", 3) + len("\n---\n")
stamp = f"\n> Version {version} — [check for a newer release]({url})\n"
doc.write_text(text[:end] + stamp + text[end:], encoding="utf-8")
PY

  zipfile="$ROOT/dist/$skill-skill.zip"
  rm -f "$zipfile"

  excludes=()
  for pattern in "${COMMON_EXCLUDES[@]}"; do excludes+=(-x "$pattern"); done
  while IFS= read -r pattern; do
    [[ -n "$pattern" ]] && excludes+=(-x "$pattern")
  done < <(skill_excludes "$skill")

  ( cd "$stage" && zip -qr "$zipfile" "$skill" "${excludes[@]}" )

  # Guard the classic packaging mistake before anyone uploads it.
  tops=$(unzip -Z1 "$zipfile" | cut -d/ -f1 | sort -u)
  if [[ "$tops" != "$skill" ]]; then
    echo "error: $zipfile has top-level entries '$tops', expected only '$skill'" >&2
    exit 1
  fi
  # grep -q would exit on the first match and SIGPIPE unzip, which pipefail
  # reports as a failure on large zips; read the whole listing instead.
  unzip -Z1 "$zipfile" | grep -x "$skill/SKILL.md" >/dev/null || {
    echo "error: $zipfile is missing $skill/SKILL.md" >&2
    exit 1
  }

  printf '%-20s %-12s %s\n' "$skill" "$display_version" "$(du -h "$zipfile" | cut -f1)"
done

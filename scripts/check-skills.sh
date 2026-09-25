#!/usr/bin/env bash
set -euo pipefail

# Checks the repo invariants from .claude/CLAUDE.md:
#   - frontmatter `name` equals the folder name
#   - every skill has agents/openai.yaml, and invocation mode agrees with SKILL.md
#   - every shipped skill is in plugin.json, README.md, README.vi.md and its bucket README
#   - in-progress skills are in none of them
#   - relative links inside each skill folder resolve

REPO="$(cd "$(dirname "$0")/.." && pwd)"
cd "$REPO"
fail=0
err() { echo "error: $*" >&2; fail=1; }

while IFS= read -r skill_md; do
  dir="$(dirname "$skill_md")"
  folder="$(basename "$dir")"
  bucket="$(basename "$(dirname "$dir")")"
  rel="./$dir"

  name="$(sed -n 's/^name: *//p' "$skill_md" | head -1 | tr -d '"')"
  [ "$name" = "$folder" ] || err "$skill_md: name '$name' != folder '$folder'"
  grep -q '^description: ' "$skill_md" || err "$skill_md: missing description"

  yaml="$dir/agents/openai.yaml"
  if [ ! -f "$yaml" ]; then
    err "$yaml missing"
  else
    user_invoked_md=no; user_invoked_yaml=no
    grep -q '^disable-model-invocation: true' "$skill_md" && user_invoked_md=yes
    grep -q 'allow_implicit_invocation: false' "$yaml" && user_invoked_yaml=yes
    [ "$user_invoked_md" = "$user_invoked_yaml" ] || err "$folder: SKILL.md and openai.yaml disagree on invocation"
  fi

  if [ "$bucket" = "in-progress" ]; then
    grep -q "$rel\"" .claude-plugin/plugin.json && err "$folder: in-progress skill listed in plugin.json"
  else
    grep -q "\"$rel\"" .claude-plugin/plugin.json || err "$folder: not in plugin.json"
    grep -qF "($rel/SKILL.md)" README.md || err "$folder: not linked from README.md"
    grep -qF "($rel/SKILL.md)" README.vi.md || err "$folder: not linked from README.vi.md"
    grep -q "(./$folder/SKILL.md)" "skills/$bucket/README.md" || err "$folder: not in skills/$bucket/README.md"
  fi

  # Relative markdown links inside the skill folder must resolve.
  while IFS= read -r md; do
    while IFS= read -r link; do
      target="${link%%#*}"
      [ -z "$target" ] && continue
      [ -e "$(dirname "$md")/$target" ] || err "$md: broken link $link"
    done < <(grep -oE '\]\(\./[^)]+\)' "$md" | sed -E 's/^\]\(//; s/\)$//')
  done < <(find "$dir" -name '*.md')
done < <(find skills -name SKILL.md | sort)

# Every plugin.json entry points at a real skill.
while IFS= read -r path; do
  [ -f "$path/SKILL.md" ] || err "plugin.json: $path has no SKILL.md"
done < <(grep -oE '"\./skills/[^"]+"' .claude-plugin/plugin.json | tr -d '"')

# The plugin version has a CHANGELOG entry, and the marketplace entry agrees on the name.
version="$(sed -n 's/^  "version": "\(.*\)",$/\1/p' .claude-plugin/plugin.json)"
[ -n "$version" ] || err "plugin.json: no version"
grep -q "^## $version\$" CHANGELOG.md || err "CHANGELOG.md: no '## $version' section for plugin.json version"
plugin_name="$(sed -n 's/^  "name": "\(.*\)",$/\1/p' .claude-plugin/plugin.json)"
grep -q "\"name\": \"$plugin_name\"" .claude-plugin/marketplace.json || err "marketplace.json: no plugin named '$plugin_name'"

[ "$fail" -eq 0 ] && echo "ok: all skill checks passed"
exit "$fail"

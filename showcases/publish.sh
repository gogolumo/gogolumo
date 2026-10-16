#!/usr/bin/env bash
# Publish Wheel and PlaySparse showcases with new Git histories.
# Requires git, GitHub CLI (gh) authenticated as gogolumo.
# Default: publish clean public showcases ONLY. Optionally close original
# source repos after mirror backups with --make-sources-private.
set -Eeuo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
EXPECTED_OWNER="gogolumo"
TEMP_DIR=""
cleanup() { if [[ -n "$TEMP_DIR" && -d "$TEMP_DIR" ]]; then rm -rf -- "$TEMP_DIR"; fi; }
trap cleanup EXIT

usage() {
  echo "Usage: bash showcases/publish.sh [--make-sources-private]"
  echo "Default creates two public repos with fresh history, but does not change source privacy."
}
[[ $# -le 1 ]] || { usage; exit 2; }
MODE="${1:-}"
[[ -z "$MODE" || "$MODE" == "--make-sources-private" ]] || { usage; exit 2; }

for tool in gh git; do
  command -v "$tool" >/dev/null 2>&1 || { echo "Missing $tool. Install and authenticate first." >&2; exit 1; }
done
gh auth status >/dev/null
LOGIN="$(gh api user --jq '.login')"
[[ "$LOGIN" == "$EXPECTED_OWNER" ]] || { echo "Refusing: authenticated as '$LOGIN', not '$EXPECTED_OWNER'." >&2; exit 1; }
git config --get user.name >/dev/null || { echo "Configure git user.name first." >&2; exit 1; }
git config --get user.email >/dev/null || { echo "Configure git user.email first." >&2; exit 1; }

# Publication and privacy cutover are separate, explicitly confirmed modes.
if [[ -z "$MODE" ]]; then
  for name in Wheel-showcase PlaySparse-showcase; do
    if gh repo view "$EXPECTED_OWNER/$name" --json name >/dev/null 2>&1; then
      echo "Refusing to overwrite existing $EXPECTED_OWNER/$name." >&2
      exit 1
    fi
  done
else
  for name in Wheel-showcase PlaySparse-showcase; do
    actual="$(gh repo view "$EXPECTED_OWNER/$name" --json visibility --jq '.visibility')"
    [[ "$actual" == "PUBLIC" ]] || { echo "$name is not public; stopping." >&2; exit 1; }
    gh api "repos/$EXPECTED_OWNER/$name/contents/README.md" --jq '.sha' >/dev/null
  done
fi

for slug in wheel playsparse; do
  src="$ROOT/$slug"
  for required in README.md index.html ASSET_PROVENANCE.md assets/ORIGINAL_PROJECT_MIT_LICENSE.txt; do
    [[ -s "$src/$required" ]] || { echo "Missing $src/$required" >&2; exit 1; }
  done
  [[ -z "$(find "$src" -type l -print -quit)" ]] || { echo "Symlink in $src: refusing publish" >&2; exit 1; }
  while IFS= read -r file; do
    rel="${file#"$src"/}"
    case "$rel" in
      README.md|index.html|ASSET_PROVENANCE.md|assets/*.png|assets/ORIGINAL_PROJECT_MIT_LICENSE.txt) ;;
      *) echo "Unreviewed file $rel. Refusing to publish." >&2; exit 1 ;;
    esac
  done < <(find "$src" -type f)
done

if [[ -z "$MODE" ]]; then
  echo "About to create TWO PUBLIC, showcase-only repositories with new Git history:"
  echo "  github.com/$EXPECTED_OWNER/Wheel-showcase"
  echo "  github.com/$EXPECTED_OWNER/PlaySparse-showcase"
  echo "No original source code or original Git history will be copied."
  read -r -p "Type PUBLISH SHOWCASES to continue: " approval
  [[ "$approval" == "PUBLISH SHOWCASES" ]] || { echo "Cancelled."; exit 0; }

TEMP_DIR="$(mktemp -d)"
for item in "wheel:Wheel-showcase" "playsparse:PlaySparse-showcase"; do
  slug="${item%%:*}"; name="${item#*:}"
  dst="$TEMP_DIR/$name"
  mkdir -p "$dst"
  cp -R "$ROOT/$slug/." "$dst/"
  git -C "$dst" init -b main >/dev/null
  git -C "$dst" add -A
  git -C "$dst" commit -m "feat: publish independent $name portfolio showcase" >/dev/null
  case "$slug" in
    wheel) description="Wheel macOS navigation — independent public showcase; no application source" ;;
    playsparse) description="PlaySparse virtual storage research — public showcase; no engine source" ;;
  esac
  gh repo create "$EXPECTED_OWNER/$name" --public --source "$dst" --remote origin --push --description "$description"
  echo "Published: https://github.com/$EXPECTED_OWNER/$name"
done

echo "Independent showcases created. Verify the images, links, markdown and responsive pages."
echo "Original Wheel and PlaySparse source repositories remain PUBLIC."
echo "After verifying both public showcases, run --make-sources-private separately."
exit 0
fi

echo
echo "WARNING: changing visibility affects contributors, forks, releases, CI, Pages and integrations."
echo "Previously published MIT grants and existing copies cannot be revoked."
echo "Review any remaining public PRs/releases and verify source ownership BEFORE proceeding."
read -r -p "Type MAKE ORIGINALS PRIVATE to continue with mirror backups and visibility changes: " confirm
[[ "$confirm" == "MAKE ORIGINALS PRIVATE" ]] || { echo "Original repositories remain public."; exit 0; }

BACKUP_ROOT="$HOME/GitHub-source-backups/$(date +%Y%m%d-%H%M%S)"
mkdir -p "$BACKUP_ROOT"
for name in Wheel PlaySparse; do
  repo="$EXPECTED_OWNER/$name"
  actual="$(gh repo view "$repo" --json visibility --jq '.visibility')"
  [[ "$actual" == "PUBLIC" ]] || { echo "$repo visibility is $actual; stopping." >&2; exit 1; }
  echo "Backing up all advertised Git refs for $repo..."
  git clone --mirror "https://github.com/$repo.git" "$BACKUP_ROOT/$name.git"
  [[ "$(git -C "$BACKUP_ROOT/$name.git" rev-parse --is-bare-repository)" == "true" ]] || exit 1
  git -C "$BACKUP_ROOT/$name.git" show-ref --heads >/dev/null
done

echo "Verified mirror backups stored in $BACKUP_ROOT"
read -r -p "Type PRIVATE SOURCE REPOS to change BOTH original repos to Private: " final
[[ "$final" == "PRIVATE SOURCE REPOS" ]] || { echo "Backups retained; original repositories remain public."; exit 0; }
for name in Wheel PlaySparse; do
  repo="$EXPECTED_OWNER/$name"
  gh repo edit "$repo" --visibility private --accept-visibility-change-consequences
  echo "$repo visibility: $(gh repo view "$repo" --json visibility --jq '.visibility')"
done
echo "Done. Check both showcases anonymously and verify no separate public releases or packages leak source."

#!/bin/sh
# Skills live once in ~/.agents/skills and are surfaced to each agent tool via
# per-skill symlinks, because Claude Code and Codex only discover personal
# skills under ~/.claude/skills and ~/.codex/skills respectively.
#
# Runs on every `chezmoi apply`: new skills are linked automatically and stale
# links (whose source skill was removed) are pruned.
#
# Safety: this only ever creates, refreshes, or removes SYMLINKS. A destination
# that is a real file or directory is left untouched -- so Codex's built-in
# .system/ skills and any tool-specific real copies are never clobbered.
set -eu

src="$HOME/.agents/skills"
[ -d "$src" ] || exit 0

for dst in "$HOME/.claude/skills" "$HOME/.codex/skills"; do
	mkdir -p "$dst"

	# Link each shared skill, but never overwrite a real file/dir.
	for d in "$src"/*/; do
		[ -d "$d" ] || continue
		name=$(basename "$d")
		target="$dst/$name"
		if [ -e "$target" ] && [ ! -L "$target" ]; then
			continue # real file/dir present -- leave it alone
		fi
		ln -sfn "../../.agents/skills/$name" "$target"
	done

	# Prune broken symlinks (skill removed from ~/.agents/skills).
	for l in "$dst"/*; do
		[ -L "$l" ] && [ ! -e "$l" ] && rm -f "$l"
	done
done

exit 0

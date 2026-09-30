---
name: notes
description: >
  Project notes journal (append-only JSONL in a Git repo). Use ONLY when the
  user explicitly asks to record something in their notes, e.g. a message that
  starts with "note:", or "prends une note", "note ça", "ajoute à mes notes",
  "mets ça dans mes notes", "take a note", "add to my notes"; to close an
  action or answer an open question in their notes; or to query their notes,
  e.g. "qu'est-ce que disent mes notes sur X", "cherche dans mes notes",
  "what do my notes say about Y". Do NOT use when the user only mentions a
  meeting, a decision or a debrief without asking to record it in their notes.
---

# Project notes (append-only JSONL + Git)

Notes live in a Git repo: `$NOTES_REPO`, or `~/GitHub/nlecoy/notes` by default.
The scripts resolve this path themselves; pass `--repo DIR` only to override it.
Scripts are in `~/.agents/skills/notes/scripts/`.

Entries are in `notes/YYYY/YYYY-MM.jsonl`, one immutable event per line.
**Never edit or delete an existing line**: the full history is the value of the
system, and Git must only see additions. To fix or complete an entry, append a
new entry that points to it.

Always write through `append_note.py`, never directly to a file. The script
validates the entry, generates `id` and `ts`, picks the monthly file, then
pulls, commits and pushes.

## Language

- Write the note content (`text`, `title`, `decisions`, `actions`, `questions`)
  in the language the user used for this note. Keep `raw` verbatim.
- Show the preview and reply in that language too.
- Keep technical terms as the user said them.
- Language-independent values: field names and `type` (English), `project`
  (reuse the existing slug), `people` (names as known), `tags` (always English,
  lowercase).

## Entry format

Fields you provide (the script adds `v`, `id`, `ts`):

| Field | Req. | Content |
|---|---|---|
| `type` | yes | `meeting`, `note`, `decision`, `action`, `correction` |
| `project` | yes | lowercase slug with hyphens: `onboarding-redesign` |
| `text` | yes | main content in Markdown, self-contained |
| `occurred_at` | no | ISO 8601, when the event did not happen just now |
| `title` | no | short title |
| `people` | no | participants; full name when known, e.g. `["Marie Dupont", "Bastien"]` |
| `tags` | no | English lowercase keywords |
| `decisions` | no | list of sentences, one decision each |
| `actions` | no | `[{"id":"a1","what":"…","owner":"…","due":"YYYY-MM-DD"}]` |
| `questions` | no | open points: `[{"id":"q1","what":"…","owner":"…"}]` |
| `resolves` | no | items this entry settles: `["<entry-id>#q1", "<entry-id>#a2"]` |
| `source` | no | `typed` or `voice` |
| `raw` | no | verbatim transcript of a spoken debrief |
| `refs` | no | related entry IDs (follow-up, context) |

Types:
- `meeting`: meeting report (often with `people`, `decisions`, `actions`).
- `note`: thought, information, progress update.
- `decision`: decision taken outside a meeting.
- `action`: legacy way to close an action (`refs` to `<id>#aN`). Use
  `resolves` on any entry instead.
- `correction`: fixes an earlier entry (`refs` = its id); `text` says what
  changes. When reading, the correction wins over the original.

`resolves` works on any entry type: a meeting note can answer an open question
and close an action in the same line.

## Adding a note

The user wants as little friction as possible. Incomplete notes are fine.

1. **Sync**: `python3 ~/.agents/skills/notes/scripts/sync_notes.py`.
   It prints the repo path, used as `<repo>` below. If it fails (offline,
   conflict), say so in one line and continue: the note will be committed
   locally and pushed later.

2. **Get known values**: `python3 ~/.agents/skills/notes/scripts/known_values.py`.
   It lists projects, people, tags, open actions and open questions. Reuse the
   exact project slugs and names ("Marie" → "Marie Dupont" if she is the only
   known Marie).

3. **Structure the content**:
   - *Typed note*: keep the user's words in `text`, `source: "typed"`.
   - *Spoken debrief* (dictated, hesitations, "euh", "um"): put the full
     transcript in `raw`, write a clean and faithful summary in `text` (invent
     nothing, keep uncertainties), `source: "voice"`.
   - Extract `people`, `decisions`, `actions` when they clearly appear.
   - Put missing or undecided points in `questions` instead of asking the user.
   - Infer `occurred_at` from hints ("ce matin", "yesterday at 2pm") using
     today's date; without a hint, omit it.

4. **Cross-reference past notes**. Read the entries of the same project and the
   entries with the same people, for example:
   ```bash
   cat <repo>/notes/*/*.jsonl | jq -c 'select(.project=="predict")'
   ```
   Also check `open_questions` and `open_actions` from step 2. Notes can be in
   different languages: match on meaning, not on words. Look for:
   - an open question that the new note answers → `resolves`
   - an open action that the new note shows as done → `resolves`
   - a follow-up of an earlier topic that stays open → `refs`
   - a decision that contradicts an earlier decision → `refs`, and say it in
     the preview
   Propose only links with a clear basis in the text. Never add them without
   the user's approval.

5. **Show the preview and wait for approval**, in a readable form:
   ```
   Note: predict - Predict sync (30/09, with Bastien)
   - Decision: …
   - Action: … (owner)
   - Open question: …

   Links to past notes (Predict meeting, 29/09):
     1. ✅ Answers "…" → answer: …
     2. 🔗 Follow-up of "…" → still open; link to the earlier note

   OK? (ok / ok except 2 / change…)
   ```
   Also flag a new project or an ambiguous name in the preview, so the user
   confirms everything with one answer. For a short and clear note without
   links, a one-line preview is enough. Only the links the user accepts go
   into `resolves` and `refs`.

6. **Write**:
   ```bash
   python3 ~/.agents/skills/notes/scripts/append_note.py <<'EOF'
   {"type":"meeting","project":"predict","title":"Predict sync","people":["Bastien"],"text":"…","questions":[{"what":"…"}],"resolves":["20260930T110540-602b#q1"],"refs":["20260930T110540-602b"],"source":"voice","raw":"…"}
   EOF
   ```
   The script prints `{"id":…, "file":…, "pushed":…}`. Confirm to the user in
   one sentence. On a validation error, fix the entry and run it again. If only
   the push failed, say the note is committed locally and will be pushed on the
   next sync.

To only close an action or answer a question, append a `note` with `resolves`
and a `text` that gives the result.

## Answering a question about the notes

1. Sync first (`sync_notes.py`). If it fails, answer from local data and say
   it may not be up to date.
2. Filter by `project`, `people` or `tags` rather than by words in `text`,
   because notes can be in different languages:
   ```bash
   cat <repo>/notes/*/*.jsonl | jq -c 'select(.project=="predict")'
   cat <repo>/notes/*/*.jsonl | jq -c 'select((.people // []) | index("Marie Dupont"))'
   ```
   `known_values.py` gives the open actions and questions of all projects.
3. Apply each `correction` to its target. An action or question is settled
   when an entry lists it in `resolves` (or, for legacy entries, in the `refs`
   of a `type: "action"` entry). Group each question with its answer.
4. Answer with the date (`occurred_at`, else `ts`) and, when useful, the `id`
   of the source entries. Separate what the notes say from what you infer. If
   the notes do not contain the answer, say so.

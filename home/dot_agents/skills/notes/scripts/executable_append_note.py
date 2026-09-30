#!/usr/bin/env python3
"""Append an entry to the JSONL notes journal (append-only), then commit/push.

Usage:
  echo '{"type":"note","project":"x","text":"..."}' | python3 append_note.py [--repo DIR] [--no-push] [--dry-run]

The script adds v, id, ts; validates the fields; pulls; writes one compact
line to notes/YYYY/YYYY-MM.jsonl; then runs git add/commit/push.
"""
import argparse, json, os, re, secrets, subprocess, sys
from datetime import datetime

SCHEMA_VERSION = 1
TYPES = {"meeting", "note", "decision", "action", "correction"}
REQUIRED = ("type", "project", "text")
OPTIONAL = {"occurred_at", "title", "people", "tags", "decisions", "actions",
            "questions", "resolves", "source", "raw", "refs"}
LIST_FIELDS = ("people", "tags", "decisions", "resolves", "refs")
ITEM_FIELDS = {"actions": "a", "questions": "q"}
SLUG = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
ITEM_REF = re.compile(r"^[^#\s]+#[aq]\d+$")


def fail(msg):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(1)


def validate(e):
    for k in REQUIRED:
        if not e.get(k):
            fail(f"missing required field: {k}")
    unknown = set(e) - set(REQUIRED) - OPTIONAL - {"v", "id", "ts"}
    if unknown:
        fail(f"unknown fields: {sorted(unknown)}")
    if e["type"] not in TYPES:
        fail(f"invalid type '{e['type']}', expected: {sorted(TYPES)}")
    if not SLUG.match(e["project"]):
        fail(f"project must be a slug (e.g. onboarding-redesign): '{e['project']}'")
    for k in LIST_FIELDS:
        if k in e and not (isinstance(e[k], list) and all(isinstance(x, str) for x in e[k])):
            fail(f"{k} must be a list of strings")
    for r in e.get("resolves", []):
        if not ITEM_REF.match(r):
            fail(f"resolves items must look like '<entry-id>#a1' or '<entry-id>#q1': '{r}'")
    for k, prefix in ITEM_FIELDS.items():
        if k not in e:
            continue
        if not isinstance(e[k], list):
            fail(f"{k} must be a list")
        for i, item in enumerate(e[k], 1):
            if not isinstance(item, dict) or not item.get("what"):
                fail(f"each item of {k} must be an object with at least 'what'")
            item.setdefault("id", f"{prefix}{i}")
    if "source" in e and e["source"] not in ("typed", "voice"):
        fail("source must be 'typed' or 'voice'")
    if "occurred_at" in e:
        try:
            datetime.fromisoformat(e["occurred_at"])
        except ValueError:
            fail("occurred_at must be an ISO 8601 date")


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--repo", default=os.environ.get("NOTES_REPO", "~/GitHub/nlecoy/notes"))
    p.add_argument("--no-push", action="store_true")
    p.add_argument("--dry-run", action="store_true", help="print the line without writing")
    args = p.parse_args()
    repo = os.path.expanduser(args.repo)

    try:
        # strict=False accepts real newlines inside strings; json.dumps escapes
        # them again, so the output stays on one line.
        entry = json.loads(sys.stdin.read(), strict=False)
    except json.JSONDecodeError as ex:
        fail(f"invalid input JSON: {ex}")
    if not isinstance(entry, dict):
        fail("the entry must be a JSON object")

    validate(entry)
    now = datetime.now().astimezone().replace(microsecond=0)
    out = {"v": SCHEMA_VERSION,
           "id": now.strftime("%Y%m%dT%H%M%S") + "-" + secrets.token_hex(2),
           "ts": now.isoformat()}
    out.update({k: v for k, v in entry.items() if k not in ("v", "id", "ts")})

    line = json.dumps(out, ensure_ascii=False, separators=(",", ":"))
    if args.dry_run:
        print(line)
        return

    git = lambda *a: subprocess.run(["git", "-C", repo, *a], capture_output=True, text=True)

    def pull():
        # Best effort: offline or on conflict, the note is still committed locally.
        if git("pull", "--rebase", "--autostash").returncode != 0:
            git("rebase", "--abort")

    if not args.no_push:
        pull()

    rel = os.path.join("notes", now.strftime("%Y"), now.strftime("%Y-%m") + ".jsonl")
    path = os.path.join(repo, rel)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "a", encoding="utf-8") as f:
        f.write(line + "\n")

    git("add", rel)
    msg = f"notes: {out['type']} {out['project']}" + (f" - {out['title']}" if out.get("title") else "")
    c = git("commit", "-m", msg)
    if c.returncode != 0:
        print(f"Note written to {rel}, but the commit failed:\n{c.stderr or c.stdout}", file=sys.stderr)
        sys.exit(2)
    if not args.no_push:
        ps = git("push")
        if ps.returncode != 0:
            # Another machine pushed in between: rebase once and retry.
            pull()
            ps = git("push")
        if ps.returncode != 0:
            print(f"Commit OK, but the push failed (the note is saved locally):\n{ps.stderr}", file=sys.stderr)
            print(json.dumps({"id": out["id"], "file": rel, "pushed": False}))
            return
    print(json.dumps({"id": out["id"], "file": rel, "pushed": not args.no_push}))


if __name__ == "__main__":
    main()

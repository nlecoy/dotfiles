#!/usr/bin/env python3
"""List projects, people and tags already in use, plus open actions and questions.

Usage: python3 known_values.py [--repo DIR]
Use it to reuse the same names before writing a new note.
"""
import argparse, glob, json, os
from collections import Counter

p = argparse.ArgumentParser()
p.add_argument("--repo", default=os.environ.get("NOTES_REPO", "~/GitHub/nlecoy/notes"))
args = p.parse_args()
repo = os.path.expanduser(args.repo)

projects, people, tags = Counter(), Counter(), Counter()
actions, questions, closed = {}, {}, set()
for path in sorted(glob.glob(os.path.join(repo, "notes", "*", "*.jsonl"))):
    with open(path, encoding="utf-8") as f:
        for n, line in enumerate(f, 1):
            if not line.strip():
                continue
            try:
                e = json.loads(line)
            except json.JSONDecodeError:
                print(f"# invalid line skipped: {path}:{n}")
                continue
            projects[e.get("project")] += 1
            people.update(e.get("people", []))
            tags.update(e.get("tags", []))
            ctx = {"project": e.get("project"), "date": e.get("occurred_at") or e.get("ts")}
            for a in e.get("actions", []):
                actions[f"{e['id']}#{a.get('id')}"] = {**a, **ctx}
            for q in e.get("questions", []):
                questions[f"{e['id']}#{q.get('id')}"] = {**q, **ctx}
            closed.update(e.get("resolves", []))
            if e.get("type") == "action":
                closed.update(e.get("refs", []))

print(json.dumps({
    "projects": [k for k, _ in projects.most_common() if k],
    "people": [k for k, _ in people.most_common()],
    "tags": [k for k, _ in tags.most_common()],
    "open_actions": {k: v for k, v in actions.items() if k not in closed},
    "open_questions": {k: v for k, v in questions.items() if k not in closed},
}, ensure_ascii=False, indent=2))

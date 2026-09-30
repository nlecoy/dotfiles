#!/usr/bin/env python3
"""Pull the latest notes, then push local commits that were not pushed yet.

Usage: python3 sync_notes.py [--repo DIR]
Prints {"repo":…, "pulled":…, "pushed":…} and exits 1 if a Git step failed.
"""
import argparse, json, os, subprocess, sys

p = argparse.ArgumentParser()
p.add_argument("--repo", default=os.environ.get("NOTES_REPO", "~/GitHub/nlecoy/notes"))
args = p.parse_args()
repo = os.path.expanduser(args.repo)

git = lambda *a: subprocess.run(["git", "-C", repo, *a], capture_output=True, text=True)
result = {"repo": repo, "pulled": False, "pushed": False}

pl = git("pull", "--rebase", "--autostash")
if pl.returncode != 0:
    git("rebase", "--abort")  # leave the repo usable; local commits stay
    result["error"] = f"pull failed: {pl.stderr.strip()}"
else:
    result["pulled"] = True
    ahead = git("rev-list", "--count", "@{u}..HEAD")
    if ahead.returncode == 0 and ahead.stdout.strip() != "0":
        ps = git("push")
        if ps.returncode != 0:
            result["error"] = f"push failed: {ps.stderr.strip()}"
        else:
            result["pushed"] = True

print(json.dumps(result))
sys.exit(1 if "error" in result else 0)

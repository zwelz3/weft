"""Maintain .claude/handoff.md across compaction and /clear.

Usage: handoff.py precompact | sessionstart

Both commands rewrite the file's "Repository state" section from git and keep
its "Notes" section unchanged. precompact prints instructions for the
compaction summary; sessionstart prints the handoff for the new context,
shortened to fit the hook output limit. Reads only the local checkout.
"""

import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HANDOFF = ROOT / ".claude" / "handoff.md"
NOTES = "## Notes"
STATE = "## Repository state"
NO_NOTES = "None recorded."
OUTPUT_LIMIT = 9000

SUMMARY_INSTRUCTIONS = """\
Keep verbatim in the summary: every branch name, commit SHA, pull request and
issue number, and the condition each pending action waits on. Keep every
instruction the person gave that is not yet a rule in AGENTS.md. Record
completed actions as completed. .claude/handoff.md is returned to the context
after compaction, so its Repository state section need not be restated."""


def git(*args):
    result = subprocess.run(
        ["git", *args], cwd=ROOT, capture_output=True, text=True, encoding="utf-8"
    )
    return result.stdout.strip() if result.returncode == 0 else ""


def notes():
    if not HANDOFF.exists():
        return NO_NOTES
    text = HANDOFF.read_text(encoding="utf-8")
    if NOTES not in text:
        return NO_NOTES
    body = text.split(NOTES, 1)[1].split(STATE, 1)[0].strip()
    return body or NO_NOTES


def base_ref():
    for ref in ("origin/main", "main"):
        if git("rev-parse", "--verify", "--quiet", ref):
            return ref
    return ""


def worktrees():
    rows = []
    path = head = branch = ""
    for line in git("worktree", "list", "--porcelain").splitlines() + [""]:
        if line.startswith("worktree "):
            path = line.removeprefix("worktree ")
        elif line.startswith("HEAD "):
            head = line.removeprefix("HEAD ")[:12]
        elif line.startswith("branch "):
            branch = line.removeprefix("branch refs/heads/")
        elif not line and path:
            dirty = len(git("-C", path, "status", "--porcelain").splitlines())
            rows.append(f"| `{path}` | `{branch or '(detached)'}` | `{head}` | {dirty} |")
            path = head = branch = ""
    return rows


def branches(base):
    rows = []
    listing = git("for-each-ref", "refs/heads", "--format=%(refname:short)\t%(upstream:short)\t%(upstream:track)")
    for line in listing.splitlines():
        name, upstream, track = (line.split("\t") + ["", ""])[:3]
        ahead = git("rev-list", "--count", f"{base}..{name}") if base else "?"
        if ahead == "0":
            continue
        pushed = f"`{upstream}` {track or '[up to date]'}" if upstream else "not pushed"
        rows.append(f"| `{name}` | {ahead} | {pushed} |")
    return rows


def state(event):
    base = base_ref()
    lines = [
        f"Written by `.claude/hooks/handoff.py` at {datetime.now(timezone.utc):%Y-%m-%dT%H:%M:%SZ} ({event}),"
        " from local refs as of the last fetch.",
        "",
        f"- Checkout: `{git('branch', '--show-current') or '(detached)'}` at `{git('log', '-1', '--format=%h %s')}`",
        f"- `{base or 'main'}`: `{git('log', '-1', '--format=%h %s', base) if base else 'not found'}`",
    ]
    status = git("status", "--porcelain").splitlines()
    lines.append(f"- Uncommitted changes: {len(status) or 'none'}")
    lines += [f"  - `{entry}`" for entry in status[:50]]
    stashes = git("stash", "list").splitlines()
    lines.append(f"- Stashes: {len(stashes) or 'none'}")
    lines += [f"  - {entry}" for entry in stashes]
    lines += ["", "| Worktree | Branch | Head | Uncommitted |", "|---|---|---|---|", *worktrees()]
    unmerged = branches(base)
    if unmerged:
        lines += ["", f"| Branch not in `{base}` | Commits ahead | Upstream |", "|---|---|---|", *unmerged]
    return "\n".join(lines)


def write(event):
    HANDOFF.parent.mkdir(parents=True, exist_ok=True)
    text = f"# Handoff\n\n{NOTES}\n\n{notes()}\n\n{STATE}\n\n{state(event)}\n"
    HANDOFF.write_text(text, encoding="utf-8")
    return text


def restored(text):
    header = (
        "Handoff from the previous context, from .claude/handoff.md. Each claim is"
        " checked against git and GitHub before it is acted on.\n\n"
    )
    if len(header) + len(text) > OUTPUT_LIMIT:
        cut = f"\n\n[Shortened to fit the hook output limit; the full text is in {HANDOFF}.]"
        text = text[: OUTPUT_LIMIT - len(header) - len(cut)] + cut
    return header + text


def main(argv):
    sys.stdout.reconfigure(encoding="utf-8")
    command = argv[1] if len(argv) > 1 else ""
    if command == "precompact":
        write("before compaction")
        print(SUMMARY_INSTRUCTIONS)
    elif command == "sessionstart":
        print(restored(write("session start")))
    else:
        print(__doc__, file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))

"""The handoff hook is wired up, keeps the agent's notes, and fits the hook output limit."""

import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRIPT = ".claude/hooks/handoff.py"


def hook_entries(event):
    settings = json.loads((ROOT / ".claude/settings.json").read_text(encoding="utf-8"))
    return settings["hooks"][event]


def commands(event):
    return [hook["command"] for entry in hook_entries(event) for hook in entry["hooks"]]


def test_hooks_run_the_script():
    assert (ROOT / SCRIPT).is_file()
    assert all(f"{SCRIPT}\" precompact" in c for c in commands("PreCompact"))
    assert all(f"{SCRIPT}\" sessionstart" in c for c in commands("SessionStart"))
    assert commands("PreCompact") and commands("SessionStart")


def test_a_failing_hook_never_exits_with_the_blocking_code():
    for command in commands("PreCompact") + commands("SessionStart"):
        assert command.endswith("|| exit 1")


def test_session_start_fires_after_compaction_and_clear():
    matchers = [entry["matcher"] for entry in hook_entries("SessionStart")]
    for source in ("compact", "clear"):
        assert any(re.search(m, source) for m in matchers)


def test_handoff_is_not_committed():
    ignored = (ROOT / ".gitignore").read_text(encoding="utf-8").splitlines()
    assert ".claude/handoff.md" in ignored


def run(repo, command):
    return subprocess.run(
        [sys.executable, str(repo / SCRIPT), command],
        capture_output=True, text=True, encoding="utf-8", check=True,
    ).stdout


def sandbox(tmp_path):
    subprocess.run(["git", "init", "-q", str(tmp_path)], check=True)
    (tmp_path / ".claude/hooks").mkdir(parents=True)
    shutil.copy(ROOT / SCRIPT, tmp_path / SCRIPT)
    return tmp_path


def test_notes_survive_and_state_is_rewritten(tmp_path):
    repo = sandbox(tmp_path)
    handoff = repo / ".claude/handoff.md"
    assert "Keep verbatim" in run(repo, "precompact")
    text = handoff.read_text(encoding="utf-8")
    assert "None recorded." in text
    handoff.write_text(text.replace("None recorded.", "Merge #99 once CI is green."), encoding="utf-8")
    restored = run(repo, "sessionstart")
    assert "Merge #99 once CI is green." in restored
    rewritten = handoff.read_text(encoding="utf-8")
    assert "Merge #99 once CI is green." in rewritten
    assert rewritten.count("## Repository state") == 1
    assert "(session start)" in rewritten


def test_restored_handoff_fits_the_output_limit(tmp_path):
    repo = sandbox(tmp_path)
    run(repo, "precompact")
    handoff = repo / ".claude/handoff.md"
    long_notes = "\n".join(f"- item {n}" for n in range(3000))
    handoff.write_text(handoff.read_text(encoding="utf-8").replace("None recorded.", long_notes), encoding="utf-8")
    restored = run(repo, "sessionstart")
    assert len(restored) <= 10_000
    assert "Shortened to fit" in restored
    assert "item 2999" in handoff.read_text(encoding="utf-8")


def test_text_outside_the_generated_block_survives(tmp_path):
    repo = sandbox(tmp_path)
    handoff = repo / ".claude/handoff.md"
    run(repo, "precompact")
    edited = handoff.read_text(encoding="utf-8").replace("## Notes", "## Next actions")
    handoff.write_text(edited + "\nAppended after the state: merge #5.\n", encoding="utf-8")
    run(repo, "sessionstart")
    rewritten = handoff.read_text(encoding="utf-8")
    assert "## Next actions" in rewritten
    assert "Appended after the state: merge #5." in rewritten
    assert rewritten.count("## Repository state") == 1
    assert "(session start)" in rewritten

"""The pinned commits agree wherever they are stated.

Decision 0002 pins sysml-toolkit and the standard library, decision 0003
pins holonic, the CI workflow builds against the first two, and STATUS.md
records all three. Each pin is read from its decision and compared with the
other artifacts, so a change to one without the others fails here. The
check reads only the checkout (AGENTS.md rule 9).
"""

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
HASH = re.compile(r"`([0-9a-f]{40})`")


def read(rel):
    return (ROOT / rel).read_text(encoding="utf-8")


def decision_hash(rel, row_marker):
    for line in read(rel).splitlines():
        if row_marker in line:
            found = HASH.findall(line)
            if found:
                return found[0]
    raise AssertionError(f"no pinned hash on a line containing {row_marker!r} in {rel}")


def test_toolkit_and_library_pins_agree():
    toolkit = decision_hash("docs/decisions/0002-sysml-toolkit-for-parsing-and-checking.md", "| sysml-toolkit |")
    library = decision_hash("docs/decisions/0002-sysml-toolkit-for-parsing-and-checking.md", "| SysML-v2-Release")
    ci = read(".github/workflows/ci.yml")
    assert f"TOOLKIT_COMMIT: {toolkit}" in ci
    assert f"LIBRARY_COMMIT: {library}" in ci
    status = read("STATUS.md")
    assert toolkit in status and library in status


def test_holonic_pin_agrees():
    text = read("docs/decisions/0003-holonic-for-graph-organization.md")
    match = re.search(r"pins holonic `main` at commit `([0-9a-f]{40})`", text)
    assert match, "decision 0003 states no holonic pin"
    pin = match.group(1)
    versions = [l for l in read("STATUS.md").splitlines() if l.startswith("| [holonic]")]
    assert versions and f"pinned at `{pin}`" in versions[0]

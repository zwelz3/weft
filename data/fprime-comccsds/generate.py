"""Regenerate this dataset from a checkout of nasa/fprime.

Usage:
    python generate.py FPRIME_CHECKOUT

FPRIME_CHECKOUT must be at the commit recorded in PROVENANCE (below), and
`fpp-to-dict` from fprime-fpp 4.0.0a2 (the version F Prime pins in its
requirements.txt) must be on PATH. The script copies the source files listed
in SOURCES, runs fpp-to-dict over the Ref deployment, and writes the ComCcsds
slice of the dictionary as instance/comccsds-dictionary.csv. Nothing is
fetched from the network.
"""

import csv
import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

PROVENANCE = "433db6e24b6509130ff50ebf7d27920ab60b04e8"

SOURCES = [
    "LICENSE.txt",
    "NOTICE.txt",
    "Svc/Subtopologies/ComCcsds/docs/sdd.md",
    "Svc/Subtopologies/ComCcsds/ComCcsds.fpp",
    "Svc/Subtopologies/ComCcsds/ComCcsdsConfig/ComCcsdsConfig.fpp",
    "Svc/ComQueue/docs/sdd.md",
    "Svc/ComQueue/ComQueue.fpp",
    "Svc/ComQueue/ComQueueCommands.fppi",
    "Svc/ComQueue/ComQueueEvents.fppi",
    "Svc/ComQueue/ComQueueTelemetry.fppi",
    "Svc/ComQueue/test/ut/ComQueueTestMain.cpp",
    "TestDeploymentsProject/Ref/Top/topology.fpp",
    "TestDeploymentsProject/Ref/Top/instances.fpp",
    "TestDeploymentsProject/Ref/Top/RefPackets.fppi",
    "docs/reference/fpp-json-dict.md",
]

# Directories whose .fpp files make up the Ref deployment's model.
MODEL_DIRS = ["Fpp", "Fw", "Svc", "Drv", "Os", "CFDP", "Utils", "default", "TestDeploymentsProject/Ref"]
EXTRA_FILES = ["cmake/platform/unix/Platform/PlatformTypes.fpp"]

# Commits that change ComQueue's requirements or tests, found with
# `git log -- Svc/ComQueue/docs/sdd.md Svc/ComQueue/test/ut/ComQueueTestMain.cpp`
# and kept where the message names an issue or a pull request.
TRACE_COMMITS = ["f70926cff2", "fa2fe5654e", "1fcade86cf", "e0beab9ded", "064fe296f2"]

REQ_ROW = re.compile(r"^\|\s*(SVC-[A-Z]+-\d{3})\s*\|(.*)\|\s*$")
TEST_BLOCK = re.compile(r"^TEST\((\w+),\s*(\w+)\)\s*\{(.*?)^\}", re.MULTILINE | re.DOTALL)
TAG = re.compile(r'REQUIREMENT\("([^"]+)"\)')

COLUMNS = [
    "kind", "name", "id", "type_or_params", "telemetryUpdate",
    "severity", "commandKind", "format", "limits", "annotation",
]


def model_files(root: Path) -> list[str]:
    files = []
    for d in MODEL_DIRS:
        for p in sorted((root / d).rglob("*.fpp")):
            rel = p.relative_to(root).as_posix()
            if "/test/" in f"/{rel}" or "/ut/" in f"/{rel}":
                continue
            files.append(rel)
    return files + EXTRA_FILES


def type_name(t) -> str:
    if not t:
        return ""
    return t.get("name", "") if isinstance(t, dict) else str(t)


def rows(dictionary: dict):
    for ch in dictionary.get("telemetryChannels", []):
        limits = ch.get("limits")
        yield {
            "kind": "telemetry", "name": ch["name"], "id": ch["id"],
            "type_or_params": type_name(ch.get("type")),
            "telemetryUpdate": ch.get("telemetryUpdate", ""),
            "format": ch.get("format", ""),
            "limits": json.dumps(limits, sort_keys=True) if limits else "",
            "annotation": flat(ch.get("annotation", "")),
        }
    for cmd in dictionary.get("commands", []):
        params = ";".join(f"{p['name']}:{type_name(p.get('type'))}" for p in cmd.get("formalParams", []))
        yield {
            "kind": "command", "name": cmd["name"], "id": cmd["opcode"],
            "type_or_params": params, "commandKind": cmd.get("commandKind", ""),
            "annotation": flat(cmd.get("annotation", "")),
        }
    for ev in dictionary.get("events", []):
        params = ";".join(f"{p['name']}:{type_name(p.get('type'))}" for p in ev.get("formalParams", []))
        yield {
            "kind": "event", "name": ev["name"], "id": ev["id"],
            "type_or_params": params, "severity": ev.get("severity", ""),
            "format": ev.get("format", ""), "annotation": flat(ev.get("annotation", "")),
        }


def cells(text: str) -> list[str]:
    return [c.strip() for c in text.split("|")]


def flat(text: str) -> str:
    return " ".join(text.split())


def write_csv(path: Path, columns: list[str], records: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=columns, lineterminator="\n")
        writer.writeheader()
        for r in records:
            writer.writerow({c: r.get(c, "") for c in columns})


def requirements(root: Path) -> tuple[list[dict], list[dict]]:
    reqs, satisfied = [], []
    queue = (root / "Svc/ComQueue/docs/sdd.md").read_text(encoding="utf-8")
    for line in queue.splitlines():
        m = REQ_ROW.match(line)
        if m:
            desc, rationale, method = cells(m.group(2))[:3]
            reqs.append({"id": m.group(1), "component": "Svc::ComQueue", "text": desc,
                         "rationale": rationale, "verification": method})
    ccsds = (root / "Svc/Subtopologies/ComCcsds/docs/sdd.md").read_text(encoding="utf-8")
    section = ""
    for line in ccsds.splitlines():
        if line.startswith("## "):
            section = line
        m = REQ_ROW.match(line)
        if not m:
            continue
        parts = cells(m.group(2))
        if "Requirements" in section:
            reqs.append({"id": m.group(1), "component": "ComCcsds", "text": parts[0],
                         "rationale": "", "verification": parts[1]})
        elif "Traceability" in section:
            satisfied.append({"requirement": m.group(1), "satisfied_by": parts[0]})
    return reqs, satisfied


def tests(root: Path) -> list[dict]:
    src = (root / "Svc/ComQueue/test/ut/ComQueueTestMain.cpp").read_text(encoding="utf-8")
    return [{"test": f"{suite}.{name}", "file": "Svc/ComQueue/test/ut/ComQueueTestMain.cpp",
             "requirements": ";".join(TAG.findall(body))}
            for suite, name, body in TEST_BLOCK.findall(src)]


def commits(root: Path) -> list[dict]:
    out = []
    for sha in TRACE_COMMITS:
        meta = subprocess.run(["git", "-C", str(root), "log", "-1", "--format=%H%x1f%ad%x1f%s", "--date=short", sha],
                              check=True, capture_output=True, text=True).stdout.strip().split("\x1f")
        diff = subprocess.run(["git", "-C", str(root), "show", "--format=", "--unified=0", sha, "--",
                               "Svc/ComQueue/docs/sdd.md", "Svc/ComQueue/test/ut/ComQueueTestMain.cpp"],
                              check=True, capture_output=True, text=True).stdout
        added = [l[1:] for l in diff.splitlines() if l.startswith("+") and not l.startswith("+++")]
        req_ids = sorted({m.group(1) for l in added if (m := REQ_ROW.match(l))})
        test_names = sorted({f"{a}.{b}" for l in added if (m := re.match(r"TEST\((\w+),\s*(\w+)\)", l))
                             for a, b in [m.groups()]})
        pr = re.search(r"\(#(\d+)\)\s*$", meta[2])
        out.append({"commit": meta[0], "date": meta[1], "subject": meta[2],
                    "pull_request": pr.group(1) if pr else "",
                    "requirement_rows_added_or_changed": ";".join(req_ids),
                    "tests_added": ";".join(test_names)})
    return out


def main(checkout: str) -> None:
    root = Path(checkout).resolve()
    head = subprocess.run(["git", "-C", str(root), "rev-parse", "HEAD"],
                          check=True, capture_output=True, text=True).stdout.strip()
    if head != PROVENANCE:
        sys.exit(f"checkout is at {head}, expected {PROVENANCE}")
    here = Path(__file__).resolve().parent

    for rel in SOURCES:
        dest = here / "source" / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(root / rel, dest)

    with tempfile.TemporaryDirectory() as out:
        subprocess.run(["fpp-to-dict", "-d", out, *model_files(root)], check=True, cwd=root)
        dictionary = json.loads((Path(out) / "RefTopologyDictionary.json").read_text(encoding="utf-8"))

    reqs, satisfied = requirements(root)
    write_csv(here / "requirements.csv", ["id", "component", "text", "rationale", "verification"], reqs)
    write_csv(here / "trace" / "satisfied-by.csv", ["requirement", "satisfied_by"], satisfied)
    write_csv(here / "trace" / "tests.csv", ["test", "file", "requirements"], tests(root))
    write_csv(here / "trace" / "commits.csv",
              ["commit", "date", "subject", "pull_request", "requirement_rows_added_or_changed", "tests_added"],
              commits(root))

    selected = [r for r in rows(dictionary) if r["name"].startswith("ComCcsds.")]
    selected.sort(key=lambda r: (r["kind"], int(r["id"])))
    target = here / "instance" / "comccsds-dictionary.csv"
    write_csv(target, COLUMNS, selected)
    print(f"{len(reqs)} requirements, {len(satisfied)} satisfied-by rows, {len(selected)} instance rows")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    main(sys.argv[1])

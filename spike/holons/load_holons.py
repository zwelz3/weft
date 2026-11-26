"""Step 7: load the normative and projected graphs into holons per decision
0003, using holonic's default in-memory rdflib backend, and validate each
holon's membrane. Each model version is its own holon (decision 0003, OQ3);
this spike has one version of one model, so it gets one holon per graph
kind (normative, projection) rather than one holon per version.

Usage: python3 load_holons.py <normative.ttl> <projection.ttl> <shapes.ttl> <out-report.md>

Needs holonic at a commit that reports untargeted nodes (zwelz3/holonic#54,
merged at 25d1c84); the report records the commit installed.
"""
import json
import sys
from collections import Counter
from importlib import metadata

import holonic

NORMATIVE_HOLON = "https://weft.ghostsystems.ai/spike1/holon/normative-pump-system"
PROJECTION_HOLON = "https://weft.ghostsystems.ai/spike1/holon/projection-pump-system"


def holonic_commit():
    """The commit pip recorded for a holonic installed from git, else
    "unknown"."""
    try:
        direct = json.loads(metadata.distribution("holonic").read_text("direct_url.json") or "{}")
    except (FileNotFoundError, json.JSONDecodeError):
        return "unknown"
    return direct.get("vcs_info", {}).get("commit_id", "unknown")


def main():
    normative_ttl, projection_ttl, shapes_ttl, report_path = sys.argv[1:5]

    ds = holonic.HolonicDataset()  # default RdflibBackend, in-memory

    ds.add_holon(NORMATIVE_HOLON, "Pump system, normative graph", holon_type="cga:DataHolon")
    ds.add_interior(NORMATIVE_HOLON, open(normative_ttl).read())
    ds.add_boundary(NORMATIVE_HOLON, open(shapes_ttl).read())

    ds.add_holon(PROJECTION_HOLON, "Pump system, projection graph", holon_type="cga:DataHolon")
    ds.add_interior(PROJECTION_HOLON, open(projection_ttl).read())

    normative_result = ds.validate_membrane(NORMATIVE_HOLON)
    projection_result = ds.validate_membrane(PROJECTION_HOLON)

    def summary(result):
        severities = Counter(u.severity for u in result.untargeted)
        return (
            f"conforms = {result.conforms}, health = {result.health.value}, "
            f"violations = {len(result.violations)}, warnings = {len(result.warnings)}, "
            f"untargeted nodes = {len(result.untargeted)} "
            f"({', '.join(f'{n} at {s}' for s, n in sorted(severities.items())) or 'none'})"
        )

    lines = [
        "# Step 7 holon load, rdflib backend\n",
        f"holonic {metadata.version('holonic')}, commit `{holonic_commit()}`.\n",
        f"Normative holon `{NORMATIVE_HOLON}`: {summary(normative_result)}\n",
        f"Projection holon `{PROJECTION_HOLON}`: {summary(projection_result)}\n",
        "## Normative holon membrane result\n",
        f"```\n{normative_result.summary()}\n```\n",
        "## Projection holon membrane result\n",
        f"```\n{projection_result.summary()}\n```\n",
        "## Holarchy summary\n",
        f"```\n{ds.holarchy_summary()}\n```\n",
    ]
    with open(report_path, "w") as f:
        f.write("\n".join(lines))

    print(f"normative: {summary(normative_result)}")
    print(f"projection: {summary(projection_result)}")
    print(f"report -> {report_path}")


if __name__ == "__main__":
    main()

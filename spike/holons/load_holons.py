"""Step 7: load the normative and projected graphs into holons per decision
0003, using holonic's default in-memory rdflib backend, and validate each
holon's membrane. Each model version is its own holon (decision 0003, OQ3);
this spike has one version of one model, so it gets one holon per graph
kind (normative, projection) rather than one holon per version.

Usage: python3 load_holons.py <normative.ttl> <projection.ttl> <shapes.ttl> <out-report.md>
                              [--backend rdflib|fuseki] [--fuseki-url URL] [--fuseki-dataset NAME]
                              [--full-result PATH]

The rdflib backend (default) is in-memory and needs nothing running. The
Fuseki backend talks to an already-running, disposable Fuseki dataset; see
BACKENDS.md for how spike 2 starts and stops one.
"""
import argparse
import json
import time
from collections import Counter
from importlib import metadata
from pathlib import Path

import holonic
from rdflib import RDF, Graph

NORMATIVE_HOLON = "https://weft.ghostsystems.ai/spike1/holon/normative-pump-system"
PROJECTION_HOLON = "https://weft.ghostsystems.ai/spike1/holon/projection-pump-system"


def build_backend(args):
    if args.backend == "rdflib":
        return None  # HolonicDataset default
    from holonic.backends.fuseki_backend import FusekiBackend

    return FusekiBackend(args.fuseki_url, dataset=args.fuseki_dataset)


def holonic_commit():
    """The commit holonic was installed from (pip's direct_url.json), or its
    version string when it was installed some other way."""
    dist = metadata.distribution("holonic")
    direct_url = dist.read_text("direct_url.json")
    if direct_url:
        commit = json.loads(direct_url).get("vcs_info", {}).get("commit_id")
        if commit:
            return commit
    return dist.version


def graph_size(ttl_text):
    g = Graph().parse(data=ttl_text, format="turtle")
    return len(g), len(set(g.subjects(RDF.type, None)))


def summarize(result):
    """Counts in place of the MembraneResult repr, whose untargeted list runs
    to one entry per typed interior node (over 100,000 characters on the
    pump-system graph)."""
    by_severity = Counter(u.severity for u in result.untargeted)
    severities = ", ".join(f"{k}: {v}" for k, v in sorted(by_severity.items())) or "none"
    return "\n".join(
        [
            f"| conforms | {result.conforms} |",
            f"| health | {result.health.value} |",
            f"| violations | {len(result.violations)} |",
            f"| warnings | {len(result.warnings)} |",
            f"| infos | {len(result.infos)} |",
            f"| untargeted nodes | {len(result.untargeted)} (by severity: {severities}) |",
        ]
    )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("normative_ttl")
    parser.add_argument("projection_ttl")
    parser.add_argument("shapes_ttl")
    parser.add_argument("report_path")
    parser.add_argument("--backend", choices=["rdflib", "fuseki"], default="rdflib")
    parser.add_argument("--fuseki-url", default="http://127.0.0.1:3030")
    parser.add_argument("--fuseki-dataset", default="ds")
    parser.add_argument(
        "--full-result",
        help="also write each holon's full MembraneResult repr (every untargeted node) to this path",
    )
    args = parser.parse_args()

    normative_ttl, projection_ttl, shapes_ttl, report_path = (
        args.normative_ttl,
        args.projection_ttl,
        args.shapes_ttl,
        args.report_path,
    )

    normative_text = Path(normative_ttl).read_text(encoding="utf-8")
    projection_text = Path(projection_ttl).read_text(encoding="utf-8")
    shapes_text = Path(shapes_ttl).read_text(encoding="utf-8")

    started = time.perf_counter()
    ds = holonic.HolonicDataset(build_backend(args))

    ds.add_holon(NORMATIVE_HOLON, "Pump system, normative graph", holon_type="cga:DataHolon")
    ds.add_interior(NORMATIVE_HOLON, normative_text)
    ds.add_boundary(NORMATIVE_HOLON, shapes_text)

    ds.add_holon(PROJECTION_HOLON, "Pump system, projection graph", holon_type="cga:DataHolon")
    ds.add_interior(PROJECTION_HOLON, projection_text)

    normative_result = ds.validate_membrane(NORMATIVE_HOLON)
    projection_result = ds.validate_membrane(PROJECTION_HOLON)

    elapsed = time.perf_counter() - started

    n_triples, n_typed = graph_size(normative_text)
    p_triples, p_typed = graph_size(projection_text)
    header = "| | |\n|---|---|"
    lines = [
        f"# Step 7 holon load, {args.backend} backend\n",
        f"holonic commit `{holonic_commit()}`. Inputs: `{normative_ttl}` ({n_triples} triples, "
        f"{n_typed} typed subjects), `{projection_ttl}` ({p_triples} triples, {p_typed} typed "
        f"subjects), boundary `{shapes_ttl}`. Load and validate took {elapsed:.2f} s (one run).\n",
        "This report gives counts. The full `MembraneResult` for each holon, with one "
        "untargeted-node entry per typed interior node, is written by rerunning this script "
        "with `--full-result <path>` (see `spike/holons/BACKENDS.md`); it is not committed.\n",
        f"## Normative holon `{NORMATIVE_HOLON}`\n",
        header,
        summarize(normative_result) + "\n",
        f"## Projection holon `{PROJECTION_HOLON}`\n",
        header,
        summarize(projection_result) + "\n",
        f"Projection report text: `{projection_result.report_text}`\n",
        "## Holarchy summary\n",
        f"```\n{ds.holarchy_summary()}\n```\n",
    ]
    Path(report_path).write_text("\n".join(lines), encoding="utf-8")
    if args.full_result:
        Path(args.full_result).write_text(
            f"{normative_result!r}\n\n{projection_result!r}\n", encoding="utf-8"
        )

    print(f"normative conforms={normative_result.conforms}; projection conforms={projection_result.conforms}")
    print(f"report -> {report_path}")


if __name__ == "__main__":
    main()

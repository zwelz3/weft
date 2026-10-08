"""Step 7: load the normative and projected graphs into holons per decision
0003, using holonic's default in-memory rdflib backend, and validate each
holon's membrane. Each model version is its own holon (decision 0003, OQ3);
this spike has one version of one model, so it gets one holon per graph
kind (normative, projection) rather than one holon per version.

Usage: python3 load_holons.py <normative.ttl> <projection.ttl> <shapes.ttl> <out-report.md>
                              [--backend rdflib|fuseki] [--fuseki-url URL] [--fuseki-dataset NAME]

The rdflib backend (default) is in-memory and needs nothing running. The
Fuseki backend talks to a already-running, disposable Fuseki dataset; see
BACKENDS.md for how spike 2 starts and stops one.
"""
import argparse

import holonic

NORMATIVE_HOLON = "https://weft.ghostsystems.ai/spike1/holon/normative-pump-system"
PROJECTION_HOLON = "https://weft.ghostsystems.ai/spike1/holon/projection-pump-system"


def build_backend(args):
    if args.backend == "rdflib":
        return None  # HolonicDataset default
    from holonic.backends.fuseki_backend import FusekiBackend

    return FusekiBackend(args.fuseki_url, dataset=args.fuseki_dataset)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("normative_ttl")
    parser.add_argument("projection_ttl")
    parser.add_argument("shapes_ttl")
    parser.add_argument("report_path")
    parser.add_argument("--backend", choices=["rdflib", "fuseki"], default="rdflib")
    parser.add_argument("--fuseki-url", default="http://127.0.0.1:3030")
    parser.add_argument("--fuseki-dataset", default="ds")
    args = parser.parse_args()

    normative_ttl, projection_ttl, shapes_ttl, report_path = (
        args.normative_ttl,
        args.projection_ttl,
        args.shapes_ttl,
        args.report_path,
    )

    ds = holonic.HolonicDataset(build_backend(args))

    ds.add_holon(NORMATIVE_HOLON, "Pump system, normative graph", holon_type="cga:DataHolon")
    ds.add_interior(NORMATIVE_HOLON, open(normative_ttl).read())
    ds.add_boundary(NORMATIVE_HOLON, open(shapes_ttl).read())

    ds.add_holon(PROJECTION_HOLON, "Pump system, projection graph", holon_type="cga:DataHolon")
    ds.add_interior(PROJECTION_HOLON, open(projection_ttl).read())

    normative_result = ds.validate_membrane(NORMATIVE_HOLON)
    projection_result = ds.validate_membrane(PROJECTION_HOLON)

    lines = [
        f"# Step 7 holon load, {args.backend} backend\n",
        f"Normative holon `{NORMATIVE_HOLON}`: membrane conforms = {normative_result.conforms}\n",
        f"Projection holon `{PROJECTION_HOLON}`: membrane conforms = {projection_result.conforms}\n",
        "## Normative holon membrane result\n",
        f"```\n{normative_result}\n```\n",
        "## Projection holon membrane result\n",
        f"```\n{projection_result}\n```\n",
        "## Holarchy summary\n",
        f"```\n{ds.holarchy_summary()}\n```\n",
    ]
    with open(report_path, "w") as f:
        f.write("\n".join(lines))

    print(f"normative conforms={normative_result.conforms}; projection conforms={projection_result.conforms}")
    print(f"report -> {report_path}")


if __name__ == "__main__":
    main()

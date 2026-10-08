"""Step 8: M1 to M6. Run from the repository root with the venv active and
SYSMLV2_CACHE_DIR set to a writable directory. Needs the sysmlv2 binary,
the SysML-v2-Release clone, and the step 3 to 7 artifacts already built
(spike/normative, spike/projection, spike/export, spike/shapes).

Usage: python3 spike/measure.py <toolkit-bin> <sysml-lib-dir> <out-dir>
"""
import json
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).parent.parent
VARIANTS = ["baseline", "rename", "insert", "move", "reorder", "extract"]


def element_ids(json_path):
    elements = json.load(open(json_path))
    return {e["elementId"] for e in elements}


def m1(toolkit, lib, out_dir):
    # IDS.md: a document's root id (and everything chained under it) derives
    # from "$root/" + source_name, where source_name is the path given on
    # the command line. Converting each variant from its own
    # spike/model/variants/<edit>/ directory would change every id on every
    # edit, including ones the edit never touched, because the source path
    # itself differs per variant -- measuring the edit's path churn, not the
    # edit's structural churn. This copies each variant's content over one
    # fixed set of file paths (a working directory) before converting, so
    # the source name is identical across every run and the id diff
    # isolates the edit.
    work_dir = out_dir / "m1-work"
    work_dir.mkdir(exist_ok=True)
    names = ("profile.sysml", "pump-library.sysml", "pump-system.sysml")
    work_paths = [work_dir / n for n in names]

    ids = {}
    for variant in VARIANTS:
        for n, wp in zip(names, work_paths):
            wp.write_text((REPO / f"spike/model/variants/{variant}/{n}").read_text())
        out = out_dir / f"m1-{variant}.json"
        subprocess.run(
            [toolkit, "convert", "--lib", lib, "--to", "full-json", *map(str, work_paths), "-o", str(out)],
            check=True,
        )
        ids[variant] = element_ids(out)

    baseline = ids["baseline"]
    rows = []
    for variant in VARIANTS[1:]:
        kept = baseline & ids[variant]
        changed = len(baseline) - len(kept)
        rows.append(
            {
                "edit": variant,
                "baseline_total": len(baseline),
                "variant_total": len(ids[variant]),
                "ids_unchanged": len(kept),
                "ids_changed_or_removed": changed,
                "pct_changed": round(100 * changed / len(baseline), 1),
            }
        )
    return rows


def m2(toolkit, lib, out_dir):
    # Two structurally identical projects under different package names.
    # IDS.md: a document root's id derives from "$root/" + source_name, the
    # path given on the command line, so two projects collide only if BOTH
    # their structure/names AND their relative source paths match. This
    # spike runs the toolkit from inside each project's own directory with
    # bare relative filenames as arguments (the natural case: two adopters
    # each naming their file e.g. "pump-library.sysml" at their repo root),
    # so source_name is the literal string "pump-library.sysml" for both --
    # isolating whether same-structure-different-package-name alone
    # collides, independent of the path-naming effect M1 controls for.
    a_dir = out_dir / "m2-project-a"
    b_dir = out_dir / "m2-project-b"
    a_dir.mkdir(exist_ok=True)
    b_dir.mkdir(exist_ok=True)

    base_library = (REPO / "spike/model/pump-library.sysml").read_text()
    base_system = (REPO / "spike/model/pump-system.sysml").read_text()
    profile = (REPO / "spike/model/profile.sysml").read_text()

    (a_dir / "profile.sysml").write_text(profile)
    (b_dir / "profile.sysml").write_text(profile)
    (a_dir / "pump-library.sysml").write_text(base_library.replace("PumpLibrary", "ProjectALibrary"))
    (b_dir / "pump-library.sysml").write_text(base_library.replace("PumpLibrary", "ProjectBLibrary"))
    (a_dir / "pump-system.sysml").write_text(
        base_system.replace("PumpSystemModel", "ProjectASystem").replace("PumpLibrary", "ProjectALibrary")
    )
    (b_dir / "pump-system.sysml").write_text(
        base_system.replace("PumpSystemModel", "ProjectBSystem").replace("PumpLibrary", "ProjectBLibrary")
    )

    out_a = (out_dir / "m2-a.json").resolve()
    out_b = (out_dir / "m2-b.json").resolve()
    subprocess.run(
        [toolkit, "convert", "--lib", lib, "--to", "full-json",
         "profile.sysml", "pump-library.sysml", "pump-system.sysml", "-o", str(out_a)],
        check=True, cwd=a_dir,
    )
    subprocess.run(
        [toolkit, "convert", "--lib", lib, "--to", "full-json",
         "profile.sysml", "pump-library.sysml", "pump-system.sysml", "-o", str(out_b)],
        check=True, cwd=b_dir,
    )
    ids_a = element_ids(out_a)
    ids_b = element_ids(out_b)
    return {
        "project_a_total": len(ids_a),
        "project_b_total": len(ids_b),
        "intersection": len(ids_a & ids_b),
    }


def m3(toolkit, lib, out_dir):
    original = REPO / "spike/model/pump-library.sysml"
    json_out = out_dir / "m3.json"
    text_out = out_dir / "m3-roundtrip.sysml"
    subprocess.run([toolkit, "convert", "--lib", lib, "--to", "compact-json", str(original), "-o", str(json_out)], check=True)
    result = subprocess.run(
        [toolkit, "convert", "--lib", lib, "--to", "text", "--min-qual", str(json_out), "-o", str(text_out)],
        capture_output=True, text=True,
    )
    original_text = original.read_text()
    roundtrip_text = text_out.read_text() if text_out.exists() else ""
    identical = original_text.strip() == roundtrip_text.strip()
    return {
        "convert_exit": result.returncode,
        "byte_identical": identical,
        "original_chars": len(original_text),
        "roundtrip_chars": len(roundtrip_text),
        "stderr": result.stderr.strip()[:2000],
    }


def _count_path_steps(path):
    # rdflib represents a property path with >1 step as a Path object
    # (SequencePath, AlternativePath, MulPath, ...); a plain URIRef predicate
    # has none. Recurses through the path's sub-paths so `(a|b)*/c` counts
    # a, b, and c as three steps.
    from rdflib.paths import AlternativePath, InvPath, MulPath, NegatedPath, Path, SequencePath

    if not isinstance(path, Path):
        return 0
    if isinstance(path, (SequencePath, AlternativePath)):
        return sum(_count_path_steps(a) if isinstance(a, Path) else 1 for a in path.args)
    if isinstance(path, MulPath):
        inner = _count_path_steps(path.path) if isinstance(path.path, Path) else 1
        return max(inner, 1)
    if isinstance(path, (InvPath, NegatedPath)):
        return 1
    return 1


def _count_triples_and_paths(algebra_node):
    # Walks a prepared query's algebra tree (BGP / TriplesBlock, and their
    # usual wrapping nodes: Filter, Project, OrderBy, Builtin_NOTEXISTS, ...)
    # and totals triple patterns and property-path steps across the whole
    # query, including inside FILTER NOT EXISTS sub-patterns.
    from rdflib.plugins.sparql.sparql import QueryContext  # noqa: F401 (import for parity, unused)

    triples = 0
    path_steps = 0
    seen = set()

    def walk(node):
        nonlocal triples, path_steps
        if isinstance(node, dict):
            if id(node) in seen:
                return
            seen.add(id(node))
            node_triples = node.get("triples")
            if node_triples is not None:
                for t in node_triples:
                    # BGP: each entry is one (s, p, o) tuple. TriplesBlock
                    # (inside FILTER NOT EXISTS, among others): each entry is
                    # a flat list of several triples' terms concatenated, in
                    # groups of 3.
                    if len(t) == 3 and not isinstance(t[0], (list, tuple)):
                        groups = [t]
                    else:
                        groups = [t[i : i + 3] for i in range(0, len(t), 3) if i + 3 <= len(t)]
                    for group in groups:
                        s, p, o = group
                        triples += 1
                        path_steps += _count_path_steps(p)
            for v in node.values():
                walk(v)
        elif isinstance(node, (list, tuple, set)):
            for v in node:
                walk(v)

    walk(algebra_node)
    return triples, path_steps


def _query_stats(rq_path, graph):
    import time

    from rdflib.plugins.sparql import prepareQuery

    text = rq_path.read_text()
    lines = sum(1 for l in text.splitlines() if l.strip() and not l.strip().startswith("#"))
    pq = prepareQuery(text)
    triples, path_steps = _count_triples_and_paths(pq.algebra)
    start = time.perf_counter()
    result = list(graph.query(pq))
    elapsed_ms = (time.perf_counter() - start) * 1000
    return {
        "lines": lines,
        "triple_patterns": triples,
        "property_path_steps": path_steps,
        "run_time_ms": round(elapsed_ms, 3),
        "rows": len(result),
    }, result


def m5(out_dir):
    import rdflib

    sys.path.insert(0, str(REPO / "spike" / "projection"))
    from project import VERIFY_LINE  # the verdict regex project.py's attach_verdicts uses

    normative = rdflib.Graph()
    normative.parse(REPO / "spike/normative/output/pump-system.ttl", format="turtle")
    projection = rdflib.Graph()
    projection.parse(REPO / "spike/projection/output.ttl", format="turtle")

    full_dir = REPO / "spike/projection/full-graph-queries"
    verify_text = (REPO / "spike/projection/verify-report.txt").read_text()

    rows = []
    for rq in sorted((REPO / "queries").glob("*.rq")):
        proj_stats, proj_result = _query_stats(rq, projection)
        full_rq = full_dir / rq.name
        full_stats, full_result = _query_stats(full_rq, normative)

        proj_rows = {tuple(str(v) for v in row) for row in proj_result}
        if rq.name == "requirement-satisfied-by.rq":
            # proj:verdict is not a graph property (project.py's
            # attach_verdicts adds it by matching `sysmlv2 verify`'s text
            # output to a claim); apply the same text match here before
            # comparing, so the equality check covers all four columns,
            # not just the three the full graph resolves by itself.
            full_rows_with_verdict = set()
            for row in full_result:
                req_name = normative.value(row.requirement, rdflib.URIRef("https://weft.ghostsystems.ai/spike1/toolkit-vocab#declaredName"))
                verdict = ""
                for line in verify_text.splitlines():
                    m = VERIFY_LINE.search(line)
                    if m and m.group("req") == str(req_name):
                        verdict = m.group("verdict").lower()
                        break
                full_rows_with_verdict.add((str(row.requirement), str(row.shortName), str(row.element), verdict))
            full_rows = full_rows_with_verdict
        else:
            full_rows = {tuple(str(v) for v in row) for row in full_result}

        rows.append(
            {
                "query": rq.name,
                "projection": proj_stats,
                "full_graph": full_stats,
                "results_equal": proj_rows == full_rows,
            }
        )
        out_path = out_dir / f"m5-{rq.stem}-full-graph-results.txt"
        out_path.write_text("\n".join(sorted(" | ".join(r) for r in full_rows)) + "\n")

    report_lines = ["# Spike 2 step 3: M5 against the full normative graph\n"]
    for row in rows:
        p, f = row["projection"], row["full_graph"]
        report_lines.append(f"## {row['query']}\n")
        report_lines.append(f"Results equal to the projected query: {row['results_equal']}\n")
        report_lines.append("| | lines | triple patterns | property-path steps | run time (ms) | rows |")
        report_lines.append("|---|---|---|---|---|---|")
        report_lines.append(
            f"| projection | {p['lines']} | {p['triple_patterns']} | {p['property_path_steps']} | {p['run_time_ms']} | {p['rows']} |"
        )
        report_lines.append(
            f"| full graph | {f['lines']} | {f['triple_patterns']} | {f['property_path_steps']} | {f['run_time_ms']} | {f['rows']} |\n"
        )
    results_md = REPO / "spike/projection/results.md"
    marker = "# Spike 2 step 3: M5 against the full normative graph"
    existing = results_md.read_text()
    base, _, _ = existing.partition(marker)
    results_md.write_text(base.rstrip() + "\n\n" + "\n".join(report_lines))
    return rows


def scheme3_capability_probe():
    # Step 4: M1/M2 for id scheme 3 need Session.from_sources_with_graph_format
    # or an equivalent Python-reachable selector; sysmlv2-py 0.10.2 wraps only
    # from_sources() (scheme 2, IDS.md's GraphFormat::LegacyV2 default). This
    # does not run M1/M2 for scheme 3; it records why not. See
    # spike/ids/probe_scheme3.py for the full inspection and
    # spike/ids/test_probe_scheme3.py for the regression fence.
    try:
        import sysmlv2
    except ImportError:
        return {"bindings_importable": False}
    return {
        "bindings_importable": True,
        "has_graph_format_selector": hasattr(sysmlv2.Session, "from_sources_with_graph_format"),
    }


def main():
    toolkit, lib, out_dir = sys.argv[1], sys.argv[2], Path(sys.argv[3])
    out_dir.mkdir(parents=True, exist_ok=True)

    print("## M1\n", m1(toolkit, lib, out_dir))
    print("## M2\n", m2(toolkit, lib, out_dir))
    print("## M3\n", m3(toolkit, lib, out_dir))
    print("## M5\n", m5(out_dir))
    print("## Scheme 3 capability probe\n", scheme3_capability_probe())


if __name__ == "__main__":
    main()

"""Step 8: measurements M1 to M6 in one run.

Run from the repository root with the venv active (rdflib, pyshacl) and
SYSMLV2_CACHE_DIR set to a writable directory:

    python3 spike/measure.py <toolkit-bin> <sysml-lib-dir> <out-dir>

<toolkit-bin> is the sysmlv2 CLI at the commit decision 0002 pins and
<sysml-lib-dir> is the SysML-v2-Release `sysml.library` directory at the
pinned library commit. Large intermediate files (full-json exports) go to
<out-dir>, as do M5's per-query results and m5-full-graph.md. The small
files that back RESULTS.md's figures are written to spike/measurements/:
m1.json and m2.json (counts, the SHA-256 of each full-json export, and
every derived id per run) and m6.json.
"""
import hashlib
import json
import shutil
import subprocess
import sys
from collections import Counter
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
MODEL = REPO / "spike/model"
# Spike 1's model. Spike 2 extended spike/model/ (RESULTS.md, "Spike 2
# results", step 2); M1 to M3 measure the model spike 1 reported on, which
# is the baseline variant, so their figures and m1.json/m2.json stay
# reproducible. M4 to M6 read the step 5 to 6 artifacts spike 2 regenerated
# from the extended model.
SPIKE1_MODEL = MODEL / "variants/baseline"
MEASUREMENTS = REPO / "spike/measurements"
NAMES = ("profile.sysml", "pump-library.sysml", "pump-system.sysml")

# M1 edits. Each compares a variant with the state it was edited from and
# names the elements the edit targets (qualified names in that state). The
# targets' ownership subtrees, together with each target's owning
# membership, are the "edited" elements; every other id in the before-state
# is "untouched". An edit that only adds elements has no edited element in
# the before-state.
M1_EDITS = [
    {
        "edit": "rename",
        "before": "baseline",
        "targets": ["PumpLibrary::PressureSensor"],
        "what": "`part def PressureSensor` renamed to `PressureTransducer`, and its one reference",
    },
    {
        "edit": "insert",
        "before": "baseline",
        "targets": [],
        "what": "`part valve : Valve` added to `PumpSystem` before `enclosure`, `part def Valve` added after `PressureSensor`",
    },
    {
        "edit": "insert-above-anonymous",
        "before": "baseline",
        "targets": [],
        "what": "`part def AuxiliaryPump` and `part auxiliaryPump` added at the top of `PumpSystemModel`, above its anonymous `satisfy` usages",
    },
    {
        "edit": "move",
        "before": "baseline",
        "targets": ["PumpSystemModel::EnclosureRating"],
        "what": "requirement `EnclosureRating` (REQ-005) moved from package `PumpSystemModel` to package `PumpLibrary`",
    },
    {
        "edit": "move-within-package",
        "before": "baseline",
        "targets": ["PumpLibrary::PumpSystem::dataLink"],
        "what": "`interface dataLink` moved from `part def PumpSystem` to `part def Pump`, both in `PumpLibrary`",
    },
    {
        "edit": "reorder",
        "before": "baseline",
        "targets": ["PumpLibrary::PumpSystem::pump", "PumpLibrary::PumpSystem::controller"],
        "what": "declaration order of `pump` and `controller` swapped in `PumpSystem`",
    },
    {
        "edit": "extract",
        "before": "extract-source",
        "targets": ["PumpSystemModel::pumpSystemUnderTest"],
        "what": "`sysmlv2 refactor extract` on `PumpSystemModel::pumpSystemUnderTest`, which gains `part def PumpSystemUnderTest :> PumpSystem`",
    },
]


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def convert(toolkit, lib, cwd, args, out):
    subprocess.run(
        [toolkit, "convert", "--lib", lib, "--to", "full-json", *args, "-o", str(out)],
        check=True,
        cwd=cwd,
    )
    return json.load(open(out, encoding="utf-8"))


def ref(value):
    return value["@id"] if isinstance(value, dict) else None


def edited_ids(elements, targets):
    """Ownership subtrees of the target elements plus each target's owning
    membership, as a set of element ids."""
    by_id = {e["@id"]: e for e in elements}
    by_qname = {e.get("qualifiedName"): e for e in elements if e.get("qualifiedName")}
    result = set()
    for qname in targets:
        root = by_qname[qname]
        membership = ref(root.get("owningRelationship"))
        if membership:
            result.add(membership)
        stack = [root["@id"]]
        seen = set()
        while stack:
            eid = stack.pop()
            if eid in seen:
                continue
            seen.add(eid)
            e = by_id[eid]
            for key in ("ownedRelationship", "ownedRelatedElement"):
                stack.extend(ref(v) for v in (e.get(key) or []) if ref(v) in by_id)
        result |= seen
    return result


IDENTITY_LINKS = ("satisfiedRequirement", "satisfyingFeature", "verifiedRequirement", "referencedFeature")


def identity_keys(elements):
    """A comparison key per element id, used to tell whether an id present
    before and after an edit still denotes the same element. The key is the
    element's metaclass, declared name, declared short name, and the names
    its satisfy, verify, and reference links point at, together with the
    same for each element it owns directly as a relationship (a membership's
    member). Positional ids can be handed to a different element after an
    edit: an OwningMembership that owned `satisfy DataLatency` before an
    insertion can own `satisfy ResponseTime` after it, under the same id."""
    by_id = {e["@id"]: e for e in elements}

    def label(i):
        target = by_id.get(i)
        return (target.get("declaredName") or target["@type"]) if target else "external"

    def own(e):
        links = []
        for key in IDENTITY_LINKS:
            value = e.get(key)
            values = value if isinstance(value, list) else [value]
            links += [(key, label(ref(v))) for v in values if ref(v)]
        return (e["@type"], e.get("declaredName"), e.get("declaredShortName"), tuple(links))

    return {
        e["@id"]: (own(e), tuple(own(by_id[ref(c)]) for c in (e.get("ownedRelatedElement") or []) if ref(c) in by_id))
        for e in elements
    }


def nearest_unnamed_kind(elements_by_id, eid):
    """Metaclass of the outermost element without a declared name or short
    name on the ownership path from `eid` up to its document root, ignoring
    relationships (which carry no names of their own). Returns None when
    every element on the path is named. A positional id segment (IDS.md)
    enters the chain at such an element."""
    found = None
    e = elements_by_id.get(eid)
    while e is not None:
        # Connectors (interface usages, binding connectors) are features
        # as well as relationships; they are counted as elements here.
        kind = e["@type"]
        is_relationship = bool(e.get("relatedElement")) and not kind.endswith(("Usage", "Connector", "Definition"))
        if not is_relationship and e["@type"] != "Namespace":
            if not e.get("declaredName") and not e.get("declaredShortName"):
                found = e["@type"]
        parent = ref(e.get("owningRelationship")) or ref(e.get("owningRelatedElement"))
        e = elements_by_id.get(parent) if parent else None
    return found


def m1(toolkit, lib, out_dir):
    # IDS.md: a document's root id, and everything chained under it, derives
    # from "$root/" + source_name, the path given on the command line. Each
    # variant's files are therefore copied over one fixed set of file names
    # in one working directory and converted from there with bare relative
    # names, so the source names are identical across every run and an id
    # difference comes from the edit, not from the path.
    work = out_dir / "m1-work"
    work.mkdir(parents=True, exist_ok=True)

    # The extract variant is the toolkit's own output: re-run the refactor
    # on extract-source and confirm the committed variant matches it.
    for n in NAMES:
        shutil.copy(MODEL / f"variants/extract-source/{n}", work / n)
    subprocess.run(
        [toolkit, "refactor", "extract", "--lib", lib, "pump-system.sysml",
         "PumpSystemModel::pumpSystemUnderTest", "pump-library.sysml", "profile.sysml"],
        check=True, cwd=work, capture_output=True,
    )
    for n in NAMES:
        committed = (MODEL / f"variants/extract/{n}").read_text(encoding="utf-8")
        if (work / n).read_text(encoding="utf-8") != committed:
            raise SystemExit(f"variants/extract/{n} differs from `sysmlv2 refactor extract` output")

    exports = {}

    def run(variant):
        if variant not in exports:
            for n in NAMES:
                shutil.copy(MODEL / f"variants/{variant}/{n}", work / n)
            out = out_dir / f"m1-{variant}.json"
            exports[variant] = (convert(toolkit, lib, work, list(NAMES), out), sha256(out))
        return exports[variant][0]

    rows = []
    for spec in M1_EDITS:
        before = run(spec["before"])
        after = run(spec["edit"])
        before_ids = {e["@id"] for e in before}
        after_ids = {e["@id"] for e in after}
        by_id = {e["@id"]: e for e in before}
        edited = edited_ids(before, spec["targets"])
        untouched = before_ids - edited
        changed_edited = edited - after_ids
        changed_untouched = untouched - after_ids
        keys_before = identity_keys(before)
        keys_after = identity_keys(after)
        reassigned = {i for i in before_ids & after_ids if keys_before[i] != keys_after[i]}
        rows.append(
            {
                "edit": spec["edit"],
                "what": spec["what"],
                "before": spec["before"],
                "before_ids": len(before_ids),
                "after_ids": len(after_ids),
                "edited_ids": len(edited),
                "edited_changed": len(changed_edited),
                "untouched_ids": len(untouched),
                "untouched_changed": len(changed_untouched),
                "edited_kept_but_reassigned": len(reassigned & edited),
                "untouched_kept_but_reassigned": len(reassigned & untouched),
                "untouched_changed_by_unnamed_ancestor": dict(
                    sorted(Counter(str(nearest_unnamed_kind(by_id, i)) for i in changed_untouched).items())
                ),
            }
        )
    return {
        "runs": {
            v: {"sha256": h, "ids": sorted(e["@id"] for e in els)}
            for v, (els, h) in sorted(exports.items())
        },
        "rows": rows,
    }


def write_project(directory, library_name, system_name):
    directory.mkdir(parents=True, exist_ok=True)
    library = (SPIKE1_MODEL / "pump-library.sysml").read_text(encoding="utf-8")
    system = (SPIKE1_MODEL / "pump-system.sysml").read_text(encoding="utf-8")
    shutil.copy(SPIKE1_MODEL / "profile.sysml", directory / "profile.sysml")
    (directory / "pump-library.sysml").write_text(
        library.replace("PumpLibrary", library_name), encoding="utf-8"
    )
    (directory / "pump-system.sysml").write_text(
        system.replace("PumpSystemModel", system_name).replace("PumpLibrary", library_name),
        encoding="utf-8",
    )


def m2(toolkit, lib, out_dir):
    # Pairs of projects compared for shared ids. IDS.md: a document root's
    # id derives from "$root/" + source_name, the path given on the command
    # line, and reusing a source name "can create duplicate root and
    # descendant IDs". Each arm fixes the package names and the source names
    # independently:
    #
    #   different-names-same-source-names: package names differ, both
    #     projects converted from inside their own directory with bare file
    #     names, so the source names are identical.
    #   same-names-root-qualified-source-names: identical package names and
    #     content under two roots, converted from their common parent so
    #     each source name carries its root (project-a/..., project-b/...).
    #   same-names-same-source-names: identical package names and content
    #     under two roots, each converted from inside its root with bare
    #     file names, so the source names are identical too.
    #   same-project-absolute-paths: one project's identical files at two
    #     checkout locations, converted with absolute paths.
    base = out_dir / "m2"
    if base.exists():
        shutil.rmtree(base)
    write_project(base / "renamed/project-a", "ProjectALibrary", "ProjectASystem")
    write_project(base / "renamed/project-b", "ProjectBLibrary", "ProjectBSystem")
    write_project(base / "same/project-a", "PumpLibrary", "PumpSystemModel")
    write_project(base / "same/project-b", "PumpLibrary", "PumpSystemModel")
    write_project(base / "checkout-1/weft", "PumpLibrary", "PumpSystemModel")
    write_project(base / "checkout-2/weft", "PumpLibrary", "PumpSystemModel")

    def bare(project_dir, label):
        out = (out_dir / f"m2-{label}.json").resolve()
        return convert(toolkit, lib, project_dir, list(NAMES), out), out

    def qualified(parent, project, label):
        out = (out_dir / f"m2-{label}.json").resolve()
        return convert(toolkit, lib, parent, [f"{project}/{n}" for n in NAMES], out), out

    def absolute(project_dir, label):
        out = (out_dir / f"m2-{label}.json").resolve()
        return convert(toolkit, lib, out_dir, [str((project_dir / n).resolve()) for n in NAMES], out), out

    arms = {
        "different-names-same-source-names": (
            bare(base / "renamed/project-a", "renamed-a"),
            bare(base / "renamed/project-b", "renamed-b"),
        ),
        "same-names-root-qualified-source-names": (
            qualified(base / "same", "project-a", "qualified-a"),
            qualified(base / "same", "project-b", "qualified-b"),
        ),
        "same-names-same-source-names": (
            bare(base / "same/project-a", "bare-a"),
            bare(base / "same/project-b", "bare-b"),
        ),
        "same-project-absolute-paths": (
            absolute(base / "checkout-1/weft", "absolute-1"),
            absolute(base / "checkout-2/weft", "absolute-2"),
        ),
    }

    result = {}
    for arm, ((els_a, out_a), (els_b, out_b)) in arms.items():
        ids_a = {e["@id"] for e in els_a}
        ids_b = {e["@id"] for e in els_b}
        shared = ids_a & ids_b
        by_id = {e["@id"]: e for e in els_a}
        result[arm] = {
            "a_ids": len(ids_a),
            "b_ids": len(ids_b),
            "shared": len(shared),
            "shared_by_document": dict(sorted(Counter(document_of(by_id, i) for i in shared).items())),
            "a_sha256": sha256(out_a),
            "b_sha256": sha256(out_b),
            "shared_ids": sorted(shared),
        }
    return result


def document_of(by_id, eid):
    """Declared name of the top-level package an element belongs to, or
    "(document root)" for a document's root Namespace and the membership
    that owns its package."""
    e = by_id[eid]
    name = None
    while e is not None:
        if e["@type"] in ("Package", "LibraryPackage") and e.get("declaredName"):
            name = e["declaredName"]
        parent = ref(e.get("owningRelationship")) or ref(e.get("owningRelatedElement"))
        e = by_id.get(parent) if parent else None
    return name or "(document root)"


def m3(toolkit, lib, out_dir):
    original = SPIKE1_MODEL / "pump-library.sysml"
    json_out = out_dir / "m3.json"
    text_out = out_dir / "m3-roundtrip.sysml"
    subprocess.run(
        [toolkit, "convert", "--lib", lib, "--to", "compact-json", str(original), "-o", str(json_out)],
        check=True,
    )
    result = subprocess.run(
        [toolkit, "convert", "--lib", lib, "--to", "text", "--min-qual", str(json_out), "-o", str(text_out)],
        capture_output=True, text=True,
    )
    original_text = original.read_text(encoding="utf-8")
    roundtrip_text = text_out.read_text(encoding="utf-8") if text_out.exists() else ""
    # check --strict on the round-tripped library together with the profile
    # it imports.
    check = subprocess.run(
        [toolkit, "check", "--strict", "--lib", lib, str(SPIKE1_MODEL / "profile.sysml"), str(text_out)],
        capture_output=True, text=True,
    )
    return {
        "convert_exit": result.returncode,
        "byte_identical": original_text == roundtrip_text,
        "original_chars": len(original_text),
        "roundtrip_chars": len(roundtrip_text),
        "matches_committed_roundtrip": roundtrip_text
        == (REPO / "spike/measurements/m3-roundtrip.sysml").read_text(encoding="utf-8"),
        "check_strict_exit": check.returncode,
        "check_strict_output": (check.stdout + check.stderr).strip()[:2000],
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


def m4(toolkit, lib, out_dir):
    library_json = out_dir / "m4-library.json"
    subprocess.run(
        [toolkit, "convert", "--lib", lib, "--to", "full-json",
         str(MODEL / "profile.sysml"), str(MODEL / "pump-library.sysml"), "-o", str(library_json)],
        check=True,
    )
    owl_out = out_dir / "m4-library.owl.ttl"
    coverage = out_dir / "m4-coverage.md"
    subprocess.run(
        [sys.executable, str(REPO / "spike/export/owl_export.py"), str(library_json),
         "https://weft.ghostsystems.ai/spike1/pump-library/", str(owl_out), str(coverage)],
        check=True, capture_output=True,
    )
    text = coverage.read_text(encoding="utf-8")
    return {
        "coverage_matches_committed": text == (REPO / "spike/export/COVERAGE.md").read_text(encoding="utf-8"),
        "owl_class_rows": text.count("| owl:Class |"),
        "object_property_rows": text.count("| owl:ObjectProperty |"),
        "not_exported_rows": text.split("## Not exported", 1)[1].count("| FeatureMembership |"),
    }


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

    report_lines = [
        "# Spike 2 step 3: M5 against the full normative graph\n",
        "Run times are one execution per query, with no warm-up or repetition. Result equality "
        "compares sets of rows.\n",
    ]
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
    # Written to out_dir, never to a tracked file, so running the test suite
    # (spike/projection/test_m5_full_graph.py) leaves the checkout unchanged.
    (out_dir / "m5-full-graph.md").write_text("\n".join(report_lines) + "\n", encoding="utf-8")
    return rows

def m6():
    sys.path.insert(0, str(REPO / "spike/shapes"))
    import validate

    return validate.measure(
        REPO / "spike/shapes/shapes.ttl",
        REPO / "spike/shapes/instances.ttl",
        REPO / "spike/shapes/instances.csv",
    )["summary"]


def scheme3_capability_probe():
    # Step 4: M1/M2 for id scheme 3 need Session.from_sources_with_graph_format
    # or an equivalent Python-reachable selector; sysmlv2-py 0.10.2 wraps none.
    # Its four Session constructors build textual sources with
    # GraphFormat::LegacyV2 (scheme 2) or, for from_compact_cbor, take the
    # format a payload already names. This does not run M1/M2 for scheme 3; it
    # records why not. See
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
    toolkit, lib, out_dir = sys.argv[1], sys.argv[2], Path(sys.argv[3]).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    results = {
        "M1": m1(toolkit, lib, out_dir),
        "M2": m2(toolkit, lib, out_dir),
        "M3": m3(toolkit, lib, out_dir),
        "M4": m4(toolkit, lib, out_dir),
        "M5": m5(out_dir),
        "M6": m6(),
        "Scheme 3 capability probe": scheme3_capability_probe(),
    }
    for key in ("M1", "M2", "M6"):
        path = MEASUREMENTS / f"{key.lower()}.json"
        path.write_text(json.dumps(results[key], indent=1) + "\n", encoding="utf-8")

    print("## M1")
    for row in results["M1"]["rows"]:
        print(" ", {k: v for k, v in row.items() if k != "what"})
    print("## M2")
    for arm, r in results["M2"].items():
        print(" ", arm, {k: v for k, v in r.items() if k not in ("shared_ids", "a_sha256", "b_sha256")})
    for key in ("M3", "M4", "M5", "M6", "Scheme 3 capability probe"):
        print(f"## {key}\n ", results[key])


if __name__ == "__main__":
    main()

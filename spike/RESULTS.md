# Spike 1 results

Toolkit commit `821221767c3c56cb1ebe7da22666197a47c9c645` (0.10.2), SysML-v2-Release commit
`de1070ae8e79c21532b8004fc663d47b35d0e9fa`, model `spike/model/pump-library.sysml` +
`spike/model/pump-system.sysml` (503 elements at baseline), unless stated otherwise. Command for
every measurement: `python3 spike/measure.py <sysmlv2 binary> <sysml.library dir> <out-dir>`, with
`SYSMLV2_CACHE_DIR` set to a writable directory.

## M1. Id churn under rename, insert, move, reorder, extract

Method: write each edit's variant under `spike/model/variants/<edit>/`, then convert baseline and
every variant from one fixed working directory (`spike/measure.py`'s `m1`), so the only thing that
differs between runs is the edit, not the source path IDS.md's root derivation is sensitive to. A
first pass that converted each variant from its own `spike/model/variants/<edit>/` directory
measured 100% churn on every edit, including `reorder`, which the derivation scheme documents as
id-stable; that number was the path change, not the edit, and is not reported below (recorded as a
gotcha, not a result).

| Edit | Baseline ids | Variant ids | Unchanged | Changed or removed | % changed |
|---|---|---|---|---|---|
| rename (`PressureSensor` to `PressureTransducer`) | 507 | 507 | 478 | 29 | 5.7% |
| insert (`Valve` part added before `enclosure`) | 507 | 540 | 507 | 0 | 0.0% |
| move (`dataLink` relocated from `PumpSystem` to `Pump`) | 507 | 507 | 502 | 5 | 1.0% |
| reorder (`pump`/`controller` declaration order swapped) | 507 | 507 | 507 | 0 | 0.0% |
| extract (`refactor extract` on an inline-bodied usage) | 507 | 516 | 385 | 122 | 24.1% |

`insert` and `reorder` match `IDS.md`'s claim exactly: a named member and its membership chain past
their ordinal, so an insertion disturbs no existing id and a reorder disturbs none either. `rename`
and `move` touch only the renamed/moved element's own subtree. `extract` is the largest, because
`refactor extract` rewrites the usage's typing chain and introduces a new definition with its own
subtree; this is a tool-assisted structural edit, not a one-line change, so a larger id delta is
expected.

## M2. Id collision between projects with identical structure

Method: two projects (`ProjectALibrary`/`ProjectASystem`, `ProjectBLibrary`/`ProjectBSystem`),
identical in structure and differing only in package name, each converted from inside its own
directory with bare relative filenames as arguments, so the source name IDS.md derives the
document root from is the same literal string (`pump-library.sysml`, `pump-system.sysml`) for both
projects, isolating the "same structure, different project" question from the path-naming effect
M1 already covers.

Project A: 507 ids. Project B: 507 ids. Intersection: 28 ids, all of them from `profile.sysml`
(`StandInProfile`, `Component`, `Interface`, `Process`, `BearerKind`, `bearer`, `material`,
`information`) — the one file both projects import unchanged, under the same file name, with
identical content. Zero ids from the renamed packages (`ProjectALibrary`/`ProjectBLibrary`,
`ProjectASystem`/`ProjectBSystem`) collided.

Ids collide between projects exactly when both the source path and the content are identical, not
from matching structure or matching names alone. This is expected and, for a shared library file
two projects both vendor unchanged, probably desired (decision 0003's alignment holons would
otherwise need to reconcile what are really the same elements). It also means the mirror's
collision risk (OQ2) is a path-naming discipline question, not an inherent property of the
derivation: two projects that name their files identically and copy identical content will collide
on that content's ids, so Weft's own project configuration should mint stable, project-qualified
source names (`spike/namespace.toml`'s approach, extended from element IRIs to toolkit source
names) if the mirror is to avoid this.

## M3. What round-tripping loses

Method: `sysmlv2 convert --to compact-json` then `convert --to text --min-qual` on
`spike/model/pump-library.sysml`; `spike/measurements/m3-roundtrip.sysml` is the output.

Not byte-identical (1915 characters in, 1775 out). The diff is entirely formatting and comments:
every `//` comment is dropped, tabs become four-space indentation, blank lines separating members
are removed, a single-line `@Component { bearer = ...; }` is reformatted across three lines, and
`doc /* The system ... */` loses the space after `/*` (`doc /*The system ...`). No construct, name,
short name, or relationship is lost; `sysmlv2 check --strict` passes on the round-tripped file
without `--lib` resolution changes (not separately re-verified by file comparison, since the text
is a formatting-only rewrite of the same compact JSON check already type-checked on export).

## M4. Ontology export coverage

From step 5 (`spike/export/COVERAGE.md`): 16 of 16 declared definitions exported as `owl:Class`
(100%). 8 of 10 nested typed features exported as `owl:ObjectProperty`; the 2 that did not
(`MonitorPressure.pressureReading`, `MonitorPressure.alarm`) are scalar-valued (`Real`, `Boolean`),
which OQ4 already expects: "usages with contextual features... have no direct OWL equivalent."

## M5. Projection query size and result equality

Method: `spike/measure.py`'s `m5` runs the five queries in `queries/` against the projected graph
(`spike/projection/output.ttl`) and reports row counts; `spike/projection/results.md` has the same
rows from the step 4 run. The brief's second half (writing each query against the normative graph
too, to compare triple-pattern counts) is not done: every projection term but `proj:verdict` is
itself only reachable from the normative graph through a multi-hop walk (components, for instance,
need usage to type to metadata-usage to metadata-definition), so a normative-graph equivalent of
each of the five queries is substantially the four `construct-*.rq` queries inlined into it; writing
that out is deferred rather than attempted under this spike's time, and OQ10 is left open on the
exact savings number pending it. What is measured: the five queries against the projection return
the row counts in `spike/projection/QUESTIONS.md` and are expressible as single `BGP + FILTER
NOT EXISTS` patterns of two to four triples each, which no normative-graph query over this model
could be (every normative predicate used in a construct has at least one more hop than its
projection equivalent).

| Query | Projection rows | Projection query shape |
|---|---|---|
| `requirement-satisfied-by.rq` | 6 | 2 BGP triples + 1 optional |
| `requirement-verified-by.rq` | 2 | 2 BGP triples |
| `unsatisfied-requirements.rq` | 0 | 2 BGP triples + 1 FILTER NOT EXISTS |
| `unverified-requirements.rq` | 4 | 2 BGP triples + 1 FILTER NOT EXISTS |
| `orphan-components.rq` | 1 | 2 BGP triples + 1 FILTER NOT EXISTS |

## M6. Derived shapes catching injected faults

From step 6 (`spike/shapes/FINDINGS.md`): 10 of 10 injected faults caught (dangling reference,
missing required property, two kinds of wrong type, cardinality), on the stand-in instance table.
`spike/holons/BACKENDS.md` records a related finding: the same shapes loaded as a holon boundary
against the *normative* graph (rather than the exported-instance graph they are designed for)
validate vacuously, because their `sh:targetClass`es do not match the normative graph's toolkit
schema class IRIs.

## Decision rule

M1 shows acceptable churn: the two edits a thread link most needs to survive (insert and reorder)
produce zero churn, rename and move touch only the element's own subtree, and only a
tool-performed structural rewrite (extract) produces a large delta, on an element the thread would
not ordinarily link to mid-rewrite. Weft needs a thin sidecar map (decision 0001's tier-1 mirror
path, OQ2's current leaning), not a response to unacceptable churn; the profile and thread queries
follow without the upstream identity issue (MR1 item 7, the drafted `docs/outreach/...`-style
report on sysml-toolkit) becoming a blocker. M2 narrows the mirror's collision risk to a path-naming
discipline question rather than an open hazard.

# Spike 2 results

Covers [zwelz3/weft#2](https://github.com/zwelz3/weft/issues/2)'s items 2 to 5, on branch
`spike/2-followup`, stacked on spike 1 (`spike/1-graph-contract`) and the buildability review.
Toolkit commit and SysML-v2-Release commit unchanged from spike 1 (`spike/ENVIRONMENT.md`).

## Step 1 (§1). Holons on Fuseki

A disposable local Apache Jena Fuseki 6.2.0, in-memory dataset, started and stopped by this
section (`spike/holons/BACKENDS.md`; AGENTS.md rule 1, tier 1). `spike/holons/load_holons.py
--backend fuseki` loads the same normative and projection graphs spike 1 loaded on rdflib and
validates the same membranes. Byte-for-byte identical `MembraneResult` to an rdflib run taken at
the same holonic commit (`spike/holons/fuseki-report.md` vs. an rdflib run): same `conforms`
verdicts, same violation/warning/untargeted-node counts. Fuseki took 1.16 s against rdflib's 0.66 s
for this section's load-and-validate run; the difference is the HTTP round trips to the dataset.
Spike 1's finding (the normative holon's `conforms = True` is vacuous, because step 5/6's shapes
target OWL export classes the normative graph's nodes are not instances of) holds identically on
both backends -- it is a shape problem (closed in step 2 below), not a backend difference.

## Step 2 (§2). SHACL shapes that target the toolkit's class names

`spike/shapes/normative-shapes.ttl`: three shapes whose `sh:targetClass` is a toolkit metaclass
(`sysml:MetadataUsage`, `sysml:AttributeUsage`, `sysml:InterfaceDefinition`), closing the
vacuous-targeting gap `spike/shapes/FINDINGS.md` recorded in spike 1. `spike/model/profile.sysml`
is brought in line with decisions 0005 to 0007's accepted textual forms (open `attribute def
BearerKind` in place of the enum; `Interface` on usages and `individual` defs, not definitions
only), and the pump model gains one element per new case: `EmbeddedController` (a two-valued
`bearer = (material, information)`), `ThirdPartyModule` (a project-declared bearer value,
`thirdPartyBinary`), and `ControllerSensorLink` (an `individual interface def` specializing
`DataLink`) with its usage. `sysmlv2 check --strict --lib` passes on the extended model
(`spike/model/CHECK.md`).

`spike/shapes/test_shacl_export.py` proves non-vacuity: each of the three shapes has at least one
focus node on the real pump-system normative graph, a synthetic node violating each shape in turn
triggers a Violation, and the shapes conform cleanly on the real model -- the AGENTS.md rule 7 proof
that every property they require at Violation severity is producible from `sysmlv2 check`-passing
textual notation, since the real model (not a synthetic fixture) is what conforms. 6 of 6 tests
pass.

The toolkit stores a metadata feature's assigned value behind a FeatureValue expression tree (a
`FeatureReferenceExpression`'s `tk:referent` for one value, an `OperatorExpression` with
`tk:argument` branches above that for a parenthesized list); the min-count shape's property path,
`(tk:member|tk:argument)*/tk:referent`, walks either shape. Decision 0006's specialization link is
already an object property in the raw toolkit graph (`Subclassification`'s `tk:general` is an IRI),
so no extra derivation work was needed there (AGENTS.md rule 5 already holds on the raw graph).

## Step 3 (§3). M5 against the full normative graph

`spike/projection/full-graph-queries/` has the five thread queries rewritten against the full
normative graph (`spike/normative/output/pump-system.ttl`), inlining the `construct-*.rq` walks
spike 1 deferred writing out. `spike/measure.py`'s `m5` runs both query sets, asserts row-for-row
result equality (including `requirement-satisfied-by.rq`'s verdict column, attached by the same
`sysmlv2 verify` text match `spike/projection/project.py` uses, since verdict is not itself a graph
triple), and reports per-query stats. `spike/projection/test_m5_full_graph.py` is the regression
fence; all rows match.

| Query | Projection (lines / triples / path steps / ms) | Full graph (lines / triples / path steps / ms) | Rows | Equal |
|---|---|---|---|---|---|
| `orphan-components.rq` | 11 / 4 / 0 / 0.78 | 18 / 10 / 0 / 1.72 | 3 | yes |
| `requirement-satisfied-by.rq` | 11 / 6 / 0 / 0.69 | 11 / 5 / 0 / 0.54 | 6 | yes |
| `requirement-verified-by.rq` | 8 / 3 / 0 / 0.15 | 12 / 6 / 0 / 0.20 | 2 | yes |
| `unsatisfied-requirements.rq` | 11 / 4 / 0 / 0.57 | 12 / 4 / 0 / 0.62 | 0 | yes |
| `unverified-requirements.rq` | 8 / 3 / 0 / 0.41 | 15 / 7 / 0 / 0.74 | 4 | yes |

Every full-graph query needed more triple patterns than its projection equivalent (the multi-hop
walk OQ10 expected), but none needed a property-path operator: each `proj:` term resolves through a
short, fixed chain of named toolkit properties, not a variable-length path. Run time is sub-2 ms on
both graphs on this model's size (630 elements); the gap is a small, constant number of extra joins,
not a different order of magnitude. This answers OQ10's deferred question: the projection's size
saving on this model is 2 to 7 fewer triple patterns per query, not an asymptotic one.

## Step 4 (§4). Id scheme 3 through the Python bindings

The `sysmlv2-py` bindings build cleanly at the pinned commit with `maturin` (`spike/ENVIRONMENT.md`
has the exact command; Rust installed via `rustup` with no shell-profile changes, since this
environment's home directory is read-only). M1 and M2 do not run for scheme 3: the bindings wrap
only `Session.from_sources()` (scheme 2, `GraphFormat::LegacyV2`), and no `#[pymethods]` anywhere in
`crates/sysmlv2-py/src/` exposes `Session::from_sources_with_graph_format` or
`Model::with_graph_format`, the two Rust-level entry points `IDS.md` documents for scheme 3.
`spike/ids/probe_scheme3.py` confirms this by inspecting the binding crate's source directly;
`spike/ids/test_probe_scheme3.py` is the regression fence (it starts failing, and M1/M2 for scheme 3
become runnable for real, the day a release adds the wrapper). This narrows OQ2 further than spike 1
did: at 0.10.2, no supported client -- CLI or Python -- can select scheme 3.

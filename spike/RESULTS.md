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
--backend fuseki` loads the normative and projection graphs this branch commits (the normative
graph has 630 typed subjects and 14,928 triples) and validates the same membranes as the rdflib
backend. Both committed reports (`spike/holons/rdflib-report.md`, `spike/holons/fuseki-report.md`)
were generated at holonic `067f5ea`, and the full `MembraneResult` reprs from the two backends are
byte-identical: same `conforms` verdicts, same health, 0 violations, 0 warnings, 0 infos, and 630
untargeted nodes for the normative holon on both. Over five runs each, rdflib took 1.42 to 1.97 s
and Fuseki 4.01 to 5.13 s for the load-and-validate run. Spike 1's finding (the normative holon's
`conforms = True` is vacuous, because step 5/6's shapes target OWL export classes the normative
graph's nodes are not instances of) holds identically on both backends, so it is a boundary
problem, not a backend difference.

holonic already detects it. `MembraneResult.untargeted` lists all 630 typed subjects of the
normative graph, at Info severity because the boundary declares no `cga:untargetedTypeSeverity`.
With `<holon> cga:untargetedTypeSeverity sh:Violation` added to the boundary, holonic reports
`conforms = True` and health compromised (`spike/holons/test_load_holons.py`). The detector is
therefore the untargeted report with a declared severity, read through health rather than
`conforms`. Step 2 below does not change this holon's boundary.

## Step 2 (§2). SHACL shapes that target the toolkit's class names

`spike/shapes/normative-shapes.ttl`: three shapes whose `sh:targetClass` is a toolkit metaclass
(`sysml:MetadataUsage`, `sysml:AttributeUsage`, `sysml:InterfaceDefinition`). Each has focus
nodes on the raw normative graph, so these three profile shapes are not vacuous there. They do not
close the membrane gap `spike/holons/BACKENDS.md` recorded in spike 1: the file is not loaded as
the normative holon's boundary, and loaded as one it targets 18 of the graph's 630 typed subjects
and leaves 612 untargeted (`spike/holons/test_load_holons.py`). A boundary that targets the whole
normative graph would need shapes for its other metaclasses or `cga:permitsType` declarations, and
the detector for what remains untargeted is holonic's untargeted report with a declared severity
(step 1).

`spike/model/profile.sysml` is brought in line with decisions 0005 to 0007's accepted textual
forms (open `attribute def BearerKind` in place of the enum; `Interface` on usages and `individual`
defs, not definitions only), and the pump model gains one element per new case:
`EmbeddedController` (a two-valued `bearer = (material, information)`), `ThirdPartyModule` (a
project-declared bearer value, `thirdPartyBinary`), and `ControllerSensorLink` (an `individual
interface def` specializing `DataLink`) with its usage. `sysmlv2 check --strict --lib` passes on the extended model
(`spike/model/CHECK.md`).

Step 5's OWL export and step 6's shapes are regenerated from the extended model. Decision 0005's
`attribute def BearerKind` is an `AttributeDefinition` and `bearer` an `AttributeUsage`, neither of
which `spike/export/owl_export.py` handled, so the export had dropped the `BearerKind` class and the
`Component_bearer` property while `spike/export/COVERAGE.md` still reported "18 declared, 18
exported", because it counted declared definitions from the exporter's own list. Coverage now
counts declared definitions from the model JSON (19), the exporter and `spike/shapes/shacl_export.py`
handle both metaclasses (19 of 19 exported), and `shacl_export.py` reads a declared
`MultiplicityRange`, so `bearer : BearerKind[1..*]` gives `sh:minCount 1` and no `sh:maxCount`.
The committed `spike/shapes/shapes.ttl` was still spike 1's and targeted `class/BearerKind` and
`property/Component_bearer`, which the export no longer produced; the regenerated file targets IRIs
the export produces. On the stand-in instance table, the regenerated shapes catch
9 of the 10 injected faults instead of 10 (`spike/shapes/FINDINGS.md`, spike 2 section).

`spike/shapes/test_shacl_export.py` tests non-vacuity on the raw graph. For each of the three
shapes, a node of the real pump-system normative graph meets the shape's SPARQL precondition (the
MetadataUsage applies Component; the AttributeUsage is a BearerKind value; the InterfaceDefinition
is `individual`), and removing or renaming what the constraint checks on that node makes it the
focus node of a Violation from that shape. A synthetic node violating each shape in turn also
triggers a Violation, and the shapes conform on the real model. Because the real model (not a
synthetic fixture) is what conforms, and each shape's constraint is evaluated on it, this is the
AGENTS.md rule 7 proof that the properties the shapes require at Violation severity are producible
from `sysmlv2 check`-passing textual notation. 10 of 10 tests in the file pass.

The toolkit stores a metadata feature's assigned value behind a FeatureValue expression tree (a
`FeatureReferenceExpression`'s `tk:referent` for one value, an `OperatorExpression` with
`tk:argument` branches above that for a parenthesized list); the min-count shape's property path,
`(tk:member|tk:argument)*/tk:referent`, walks either shape. Decision 0006's specialization link is
already an object property in the raw toolkit graph (`Subclassification`'s `tk:general` is an IRI),
so no extra derivation work was needed there (AGENTS.md rule 5 already holds on the raw graph).

`BearerValueAlignmentAxiomShape` stands in for decision 0005's "every value has exactly one
alignment axiom" with a list of registered value names in a `NOT IN` filter. It detects a value
with no axiom. It cannot detect a value with two, because a name list has no way to represent a
duplicate registration; that half of the rule waits for an alignment file asserted as data, against
which a shape can count axioms per value.

## Step 3 (§3). M5 against the full normative graph

`spike/projection/full-graph-queries/` has the five thread queries rewritten against the full
normative graph (`spike/normative/output/pump-system.ttl`), inlining the `construct-*.rq` walks
spike 1 deferred writing out. `spike/measure.py`'s `m5` runs both query sets, compares the result
sets of rows, and writes per-query stats to `<out-dir>/m5-full-graph.md` (no tracked file is
written). `spike/projection/test_m5_full_graph.py` is the regression fence; all five comparisons
are equal.

| Query | Projection (lines / triples / path steps / ms) | Full graph (lines / triples / path steps / ms) | Triple patterns, full minus projection | Rows | Equal |
|---|---|---|---|---|---|
| `orphan-components.rq` | 11 / 4 / 0 / 0.78 | 18 / 10 / 0 / 1.72 | +6 | 3 | yes |
| `requirement-satisfied-by.rq` | 11 / 6 / 0 / 0.69 | 11 / 5 / 0 / 0.54 | -1 | 6 | yes |
| `requirement-verified-by.rq` | 8 / 3 / 0 / 0.15 | 12 / 6 / 0 / 0.20 | +3 | 2 | yes |
| `unsatisfied-requirements.rq` | 11 / 4 / 0 / 0.57 | 12 / 4 / 0 / 0.62 | 0 | 0 | yes |
| `unverified-requirements.rq` | 8 / 3 / 0 / 0.41 | 15 / 7 / 0 / 0.74 | +4 | 4 | yes |

Run times are one execution per query, with no warm-up or repetition. They do not support a
comparison between the two graphs: a later check that ran each query 51 times in another session
gave medians from 0.51 to 2.81 ms on the projection and from 0.88 to 6.43 ms on the full graph, with
the full-graph `orphan-components.rq` the slowest. Those repeated runs are not committed.

Three of the five full-graph queries needed more triple patterns than their projection
equivalents (3, 4, and 6 more: the usage-to-definition and verification-membership walks the
projection flattens). `unsatisfied-requirements.rq` needed the same number, and
`requirement-satisfied-by.rq` needed one fewer, because the projected query's `OPTIONAL { ?claim
proj:verdict ?verdict }` has no counterpart in the graph and `m5` attaches the verdict outside the
query (below). None needed a property-path operator: each `proj:` term resolves through a short,
fixed chain of named toolkit properties, not a variable-length path. This answers OQ10's deferred
question for this model (630 typed elements): a projected query ranges from one triple pattern
longer to six shorter than its full-graph equivalent, a small, fixed number of joins rather than an
asymptotic difference.

Three limits on the equality column. Equality compares sets of rows, so it does not check row order
or duplicate rows. `unsatisfied-requirements.rq` returns 0 rows on both graphs, so its equality is
vacuous on this model. For `requirement-satisfied-by.rq`, the verdict column is not a graph triple:
`m5` attaches it to the full-graph rows by the same `sysmlv2 verify` text match
`spike/projection/project.py` uses for the projection, so the verdict column agrees by construction
and the comparison is independent evidence for the other three columns only.

## Step 4 (§4). Id scheme 3 through the Python bindings

The `sysmlv2-py` bindings build cleanly at the pinned commit with `maturin` (`spike/ENVIRONMENT.md`
has the exact command; Rust installed via `rustup` with no shell-profile changes, since this
environment's home directory is read-only). M1 and M2 do not run for scheme 3. The bindings expose
four `Session` constructors: `from_files`, `from_sources`, and `from_interchange_json` build with
`GraphFormat::LegacyV2` (scheme 2), and `from_compact_cbor` takes the graph format a CBOR payload's
header names, so it can open a scheme-3 payload but cannot produce one from textual notation. No
`#[pymethods]` in `crates/sysmlv2-py/src/` wraps `Session::from_sources_with_graph_format` (in
`sysmlv2-transform`) or `Model::with_graph_format` (in `sysmlv2-model`), the two Rust-level entry
points `IDS.md` documents for scheme 3. `spike/ids/probe_scheme3.py` confirms this by inspecting the
binding crate's source; `spike/ids/test_probe_scheme3.py` repeats the inspection against the
checkout `WEFT_TOOLKIT_SRC` names and checks the installed wheel's constructor names. Pointed at a
later release's checkout, it fails if that release's binding crate mentions a graph-format API. This
narrows OQ2 further than spike 1 did: at 0.10.2, neither the CLI nor the Python bindings can build a
scheme-3 model from textual notation.

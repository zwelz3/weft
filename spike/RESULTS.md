# Spike 1 results

Toolkit commit `821221767c3c56cb1ebe7da22666197a47c9c645` (0.10.2), SysML-v2-Release commit
`de1070ae8e79c21532b8004fc663d47b35d0e9fa`, model `spike/model/profile.sysml`,
`spike/model/pump-library.sysml`, and `spike/model/pump-system.sysml` as spike 1 left them (507
elements in the toolkit's full-json export), unless stated otherwise. Spike 2 extended those files
to 630 elements ("Spike 2 results", step 2); spike 1's version of the three files is
`spike/model/variants/baseline/`, which M1 to M3 read. M4 to M6 read the step 4 to 6 artifacts,
which spike 2 regenerated from the extended model, so each of those sections says where a re-run on
the current files differs from spike 1's figure.

## Reproducing the measurements

One command runs M1 to M6:

```
python3 spike/measure.py <sysmlv2 binary> <sysml.library dir> <out-dir>
```

run from the repository root, with `SYSMLV2_CACHE_DIR` set to a writable directory and a Python
environment holding rdflib and pySHACL (`spike/ENVIRONMENT.md` lists the versions). M1 to M4 call
the toolkit; M4, M5, and M6 also read the step 4 to 6 artifacts already committed under
`spike/projection/`, `spike/export/`, and `spike/shapes/`. The script writes the full-json exports
(about 1.2 MB each) and M5's per-query results to `<out-dir>` and the files that back the figures
below to `spike/measurements/`: `m1.json` and `m2.json` (counts, the SHA-256 of every full-json export, and
the ids compared) and `m6.json`. The figures in this document are from the run with the binary
built from source at the pinned commit (`spike/ENVIRONMENT.md`, "Re-run for the review fixes").

## M1. Id churn under rename, insert, move, reorder, extract

Method: each edit is a variant under `spike/model/variants/<edit>/`, compared with the state it was
edited from. Baseline and every variant are converted from one fixed working directory with bare
file names (`spike/measure.py`'s `m1`), because `IDS.md` derives a document's root id, and every id
chained under it, from the source name given on the command line; with the source names fixed, an
id difference comes from the edit and not from the path. A first pass that converted each variant
from its own directory changed every id on every edit, including `reorder`, and is not reported.

The elements an edit targets, with their ownership subtrees and owning memberships, are the
"edited" ids; every other id in the before-state is "untouched". An id counts as changed when it is
absent after the edit. An id present after the edit can still denote a different element, because
positional ids are reassigned when siblings shift; `spike/measure.py`'s `identity_keys` compares
each kept id's metaclass, names, and satisfy/verify/reference targets before and after, and a kept
id whose element differs is counted as reassigned.

| Edit | Before-state ids | Edited ids: changed, reassigned | Untouched ids: changed, reassigned |
|---|---|---|---|
| `rename`: `part def PressureSensor` to `PressureTransducer` | 507 | 29 of 29, 0 | 0 of 478, 0 |
| `insert`: `part valve` added to `PumpSystem` before `enclosure`, `part def Valve` added | 507 | none edited | 0 of 507, 0 |
| `insert-above-anonymous`: `part def AuxiliaryPump` and `part auxiliaryPump` added at the top of `PumpSystemModel` | 507 | none edited | 122 of 507, 4 |
| `move`: requirement `EnclosureRating` (REQ-005) moved from package `PumpSystemModel` to package `PumpLibrary` | 507 | 7 of 10, 3 | 122 of 497, 4 |
| `move-within-package`: `interface dataLink` moved from `part def PumpSystem` to `part def Pump` | 507 | 5 of 5, 0 | 0 of 502, 0 |
| `reorder`: `pump` and `controller` swapped in `PumpSystem` | 507 | 0 of 8, 0 | 0 of 499, 0 |
| `extract`: `sysmlv2 refactor extract` on `PumpSystemModel::pumpSystemUnderTest` | 511 (`extract-source`) | 4 of 8, 0 | 121 of 503, 5 |

The `extract` variant is the toolkit's own output. The baseline has no usage with an inline body,
which `refactor extract` requires, so `extract-source` is the baseline with a one-attribute body
added to `pumpSystemUnderTest`; `refactor extract` then produces `part def PumpSystemUnderTest :>
PumpSystem` holding that body and retypes the usage. `measure.py` re-runs the refactor and fails if
its output differs from the committed `variants/extract/`. The variant formerly named `extract`
inserted a definition and a usage by hand and extracted nothing; it is now
`insert-above-anonymous`. The variant formerly named `move` stayed inside one package; it is now
`move-within-package`, and `move` crosses packages as issue #2 specifies.

Two patterns account for every changed or reassigned untouched id in the table:

- An edit confined to named elements changes only the edited subtree. `rename`, `insert`,
  `move-within-package`, and `reorder` change no untouched id, as `IDS.md` states: a named member and
  its membership chain past their ordinal.
- An edit that adds or removes a member in `PumpSystemModel` above its six `satisfy` usages changes
  every id in those usages' ownership subtrees (120 ids) and 1 or 2 of the memberships that own
  them, and hands the other 4 or 5 membership ids to different `satisfy` usages. The `satisfy`
  usages are positional because, under `IDS.md`'s id-name rule, a `satisfy` usage takes the name of the requirement it
  references, and the requirement of that name precedes it in the same package; the later claimant
  of a name falls back to a positional segment. `move` shows the rule directly: once `EnclosureRating`
  leaves `PumpSystemModel`, the `satisfy EnclosureRating` usage takes over the requirement's former
  id, which is 1 of the 3 reassigned edited ids.

`insert` shows no untouched churn because no positional element follows either of its insertion
points; `IDS.md` states that an insertion disturbs positional later siblings, which is what
`insert-above-anonymous` measures. `extract` keeps the id of the usage it retypes (its name is
unchanged) and changes the ids of the body it moves into the new definition; its untouched churn
comes from the new definition's membership, inserted above the `satisfy` usages.

The thread links to `satisfy` claims: `proj:SatisfyClaim` is minted from the claim's element id
(`docs/graph-contract.md`), so each of the three edits of the second kind changed the IRI of all six
satisfy claims. A sidecar map keyed by qualified name, as OQ2 currently proposes, has no key for a
`satisfy` usage, which has no declared name.

## M2. Id collision between projects

Method: pairs of projects built from the pump model, each pair converted twice and the id sets
intersected (`spike/measure.py`'s `m2`). The arms vary the package names and the source names
independently, because `IDS.md` roots each document's ids in its source name and states that
"reusing a name can create duplicate root and descendant IDs".

| Arm | Package names | Source names | Shared ids |
|---|---|---|---|
| Different names, same source names | `ProjectALibrary`/`ProjectASystem` and `ProjectBLibrary`/`ProjectBSystem`; profile unchanged | Bare file names, each converted from inside its own directory | 28 of 507 |
| Same names, root-qualified source names | Identical | `project-a/pump-library.sysml` and `project-b/pump-library.sysml`, converted from the common parent | 0 of 507 |
| Same names, same source names | Identical | Bare file names, each converted from inside its own directory | 507 of 507 |
| One project at two checkout locations | Identical | Absolute paths | 0 of 507 |

The 28 shared ids in the first arm are the root `Namespace` of each of the three documents, the
membership that owns `StandInProfile`, and the 24 elements inside `StandInProfile`, the one file
both projects carry unchanged. No id inside the renamed packages is shared. In the third arm the two
full-json exports are byte-identical (the same SHA-256 in `spike/measurements/m2.json`), so two
projects that use the same package names and the same source names cannot be told apart by id.

A document's root id collides whenever the source names agree, and an id below the root collides
when the source name and the content along its id chain agree; no id collides when the source names
differ, whatever the package names. The fourth arm applies this to one project: converted from two
checkout locations with absolute paths, its two runs share no id, so element ids, and the element
IRIs minted from them, depend on how the CLI was given the source path. Which source name a project
uses is therefore part of its identity.

## M3. What round-tripping loses

Method: `sysmlv2 convert --to compact-json` then `convert --to text --min-qual` on
spike 1's `pump-library.sysml` (`spike/model/variants/baseline/pump-library.sysml`); `spike/measurements/m3-roundtrip.sysml` is the output, and
`measure.py` checks that a re-run reproduces it.

Not byte-identical (1915 characters in, 1775 out). The diff is formatting and comments: every `//`
comment is dropped, tabs become four-space indentation, blank lines separating members are removed,
a single-line `@Component { bearer = ...; }` is reformatted across three lines, and
`doc /* The system ... */` loses the space after `/*` (`doc /*The system ...`). No construct, name,
short name, or relationship in the file is lost. `sysmlv2 check --strict --lib <lib>
spike/model/variants/baseline/profile.sysml spike/measurements/m3-roundtrip.sysml` exits 0 with no
output.

M3 round-trips the library file only. `pump-system.sysml`'s constructs (`satisfy` and `verify`
usages, feature chains such as `pumpSystemUnderTest.pump`, and `:>>` redefinition) are not
round-tripped, so the result says nothing about them.

## M4. Ontology export coverage

From step 5 (`spike/export/COVERAGE.md`; `measure.py` re-runs the export and checks the table):
16 of 16 declared definitions exported as `owl:Class`. 9 of 11 nested typed features exported as
`owl:ObjectProperty` (8 in `PumpLibrary` and `Component.bearer` in the profile). The two that did
not, `MonitorPressure.pressureReading` (`Real`) and `MonitorPressure.alarm` (`Boolean`), are
scalar-valued, and `owl_export.py` emits no property for a feature whose type is not an exported
class. OWL can express both as `owl:DatatypeProperty` with an XSD range, so this is a gap in the
exporter, not an instance of OQ4's statement that usages with contextual features have no OWL
equivalent.

Three parts of OQ4 are not exercised. The library declares no specialization between exported
classes, so no `rdfs:subClassOf` is emitted and that derivation is untested. The export emits no
`owl:Ontology`, `owl:versionIRI`, or `owl:imports`. No usage with contextual features,
redefinition in context, or feature chain is in the library.

These figures are spike 1's. On spike 2's extended model the committed `COVERAGE.md`, which
`measure.py`'s check now compares with, reports 19 of 19 declared definitions exported and the same
9 of 11 nested typed features ("Spike 2 results", step 2). The extended library declares one
specialization, `ControllerSensorLink :> DataLink`, and its export emits the one `rdfs:subClassOf`
triple for it, so the specialization derivation is exercised once on that model.

## M5. Projection query size and result equality

Method: `spike/measure.py`'s `m5` runs the five queries in `queries/` against the projected graph
(`spike/projection/output.ttl`) and reports row counts; `spike/projection/results.md` has the same
rows from the step 4 run. The brief's second half (writing each query against the normative graph
too, to compare triple-pattern counts) was not attempted in this spike. Every projection term but
`proj:verdict` is reachable from the normative graph only through a multi-hop walk (components, for
instance, need usage to type to metadata-usage to metadata-definition), so a normative-graph
equivalent of each of the five queries is substantially the four `construct-*.rq` queries inlined
into it. OQ10 stays open on the size of the saving. What is measured: the five queries against the
projection return the row counts in `spike/projection/QUESTIONS.md` and are expressible as single
`BGP + FILTER NOT EXISTS` patterns of two to four triples each.

| Query | Projection rows | Projection query shape |
|---|---|---|
| `requirement-satisfied-by.rq` | 6 | 2 BGP triples + 1 optional |
| `requirement-verified-by.rq` | 2 | 2 BGP triples |
| `unsatisfied-requirements.rq` | 0 | 2 BGP triples + 1 FILTER NOT EXISTS |
| `unverified-requirements.rq` | 4 | 2 BGP triples + 1 FILTER NOT EXISTS |
| `orphan-components.rq` | 1 | 2 BGP triples + 1 FILTER NOT EXISTS |

On spike 2's extended model the committed projection returns 3 rows for `orphan-components.rq`
(the pressure sensor, `embeddedControllerUnderTest`, and `thirdPartyModuleUnderTest`, the two
components spike 2 adds with no `satisfy` claim) and the same counts for the other four queries.
Spike 2 step 3 wrote the normative-graph side and counts triple patterns from each query's algebra,
including those inside OPTIONAL and FILTER NOT EXISTS: 3 to 6 per query on the projection. That
count replaces the shape column above, which undercounts the basic graph patterns of
`requirement-satisfied-by.rq` (5 triple patterns) and `requirement-verified-by.rq` (3).

## M6. Derived shapes catching injected faults

From step 6 (`spike/shapes/FINDINGS.md`, regenerated by `spike/shapes/validate.py`). On the stand-in
instance table, each of the 10 injected faults (dangling reference, missing required property, two
kinds of wrong value, cardinality) has a validation result on the property the fault concerns.

The shapes also flag 10 of the 18 clean rows (56%): every `PumpSystem`, `Pump`, and `Controller`
row. The cause is that `shacl_export.py` derives `sh:minCount 1` for every nested typed feature,
because the model declares no multiplicity, and that includes the port and interface features
`PumpSystem.powerIn`, `PumpSystem.dataLink`, `Pump.powerPort`, and `Controller.dataPort`; the table
has no columns for them, so no row supplies a value. 20 of the 30 validation results come from
those four shapes. The step 6 run counted a fault as caught when its row had any result, which on
this table would have counted a fault on a `PumpSystem`, `Pump`, or `Controller` row as caught
whatever the fault; the count above requires a result on the fault's own property.

These are spike 1's shapes. Spike 2 regenerated `spike/shapes/shapes.ttl` from the extended model,
where `bearer` is `BearerKind[1..*]` ("Spike 2 results", step 2). On the regenerated shapes the same
count gives 8 of the 10 faults caught on their own property and the same 10 of 18 clean rows
flagged, with 28 validation results; the two rows not caught carry two distinct bearer values,
which decision 0005 allows, so they are no longer faults. `spike/measurements/m6.json` and the
generated part of `spike/shapes/FINDINGS.md` hold this run.

No injected row carries a wrong `rdf:type` (`wrong_bearer_type` is a wrong value type), so M6 does
not exercise OQ6's case of a record that arrives with the wrong type.

Step 7 (`spike/holons/BACKENDS.md`) loaded the same shapes as the boundary of a holon over the
normative graph. They validate vacuously there, because their `sh:targetClass`es do not match the
normative graph's class IRIs. Step 7 first ran on holonic `d8d1758`, which predates the
untargeted-node report ([zwelz3/holonic#54](https://github.com/zwelz3/holonic/pull/54)) and
[zwelz3/holonic#56](https://github.com/zwelz3/holonic/pull/56). Re-run on holonic `067f5ea`: the
normative holon reports `conforms = True`, health `intact`, no violations, and 507 untargeted nodes
at Info severity, which is every typed node in spike 1's graph (630 on spike 2's extended graph,
step 1 below). The report now shows the vacuous pass; at the default Info severity it does not
lower the holon's health.

## Decision rule

The rule in `docs/reviews/2026-10-08-review-summary.md` section 4: if M1 shows acceptable churn,
Weft needs only a thin sidecar map; if not, the upstream identity issue (MR1 item 7,
`docs/outreach/sysml-toolkit-rename-stable-identity.md`) becomes a blocker for identity. The rule
does not define "acceptable", and the evidence does not settle it mechanically, so the choice is
left to the maintainer. What the evidence shows:

- Edits confined to named elements (rename, insert among named members, move within a package,
  reorder) change only the edited subtree. A map keyed by qualified name or short name can follow
  them.
- Adding, removing, or extracting a member in a package that also holds `satisfy` usages changes
  every id inside those usages and reassigns surviving positional ids to different elements
  (122 changed and 4 reassigned for an insertion, 121 and 5 for `refactor extract`). Moving a
  requirement out of the package hands its id to a `satisfy` usage. An id-keyed map cannot detect a
  reassignment from the id alone, and a qualified-name-keyed map has no key for a `satisfy` usage.
- The thread's `satisfy` claims are minted from element ids, so their IRIs change under the second
  kind of edit on this model.
- M2: ids collide exactly when source names and content agree, and the same project converted from
  two checkout locations with absolute paths shares no id. The source name a project passes to the
  toolkit is part of element identity.

Open, for the decision: whether a sidecar map that identifies a `satisfy` claim by its requirement
and satisfying element (rather than by toolkit id) is sufficient, or whether the upstream issue
becomes a blocker; and whether Weft fixes the source names it passes to the toolkit. M1 and M2 ran
on scheme 2, the only scheme the CLI emits; scheme 3 is unmeasured.

## Generated outputs

`spike/normative/output/pump-system.ttl` (14,928 triples, 630 typed subjects, from spike 2's
extended model; 12,068 triples and 507 typed subjects on spike 1's model) is regenerated
byte-for-byte by converting the three model files from the repository root with the toolkit and
running `spike/normative/convert.py <full.json> pump-system spike/namespace.toml <out.ttl>`.

The step 3 graph of the public model, `quadcopter.ttl`, is not committed, because it is used only
for its triple count. The committed file had 98,433 triples and 4,061 typed subjects, SHA-256
`82b395cea0aa9da1edcd41cb63a74dc7051af54b61fb9158cbb17fc9ac267f89`
(`spike/normative/output/quadcopter.ttl.sha256`). Regenerate it with

```
sysmlv2 convert --lib <sysml.library dir> --to full-json \
  "<SysML-v2-Release>/sysml/src/examples/Geometry Examples/SimpleQuadcopter.sysml" -o quadcopter.json
SYSMLV2_TOOLKIT_SRC=<sysml-toolkit checkout> python3 spike/normative/convert.py \
  quadcopter.json quadcopter spike/namespace.toml spike/normative/output/quadcopter.ttl
```

A regeneration from another source path has the same triple and subject counts and different
element IRIs, as M2's fourth arm predicts: one run with the absolute path of a different clone
shared none of the 4,061 subject IRIs. The source path of the original run was not recorded, so the
committed bytes cannot be reproduced.

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

holonic already detects it, as spike 1's step 7 re-run found on spike 1's graph (M6 above).
`MembraneResult.untargeted` lists all 630 typed subjects of the
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
8 of the 10 injected faults on the faulty property instead of 10, or 9 of 10 counting any result on
the row (`spike/shapes/FINDINGS.md`, spike 2 section; M6 above).

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

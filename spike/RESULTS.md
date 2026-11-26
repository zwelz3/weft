# Spike 1 results

Toolkit commit `821221767c3c56cb1ebe7da22666197a47c9c645` (0.10.2), SysML-v2-Release commit
`de1070ae8e79c21532b8004fc663d47b35d0e9fa`, model `spike/model/profile.sysml`,
`spike/model/pump-library.sysml`, and `spike/model/pump-system.sysml` (507 elements in the toolkit's
full-json export), unless stated otherwise.

## Reproducing the measurements

One command runs M1 to M6:

```
python3 spike/measure.py <sysmlv2 binary> <sysml.library dir> <out-dir>
```

run from the repository root, with `SYSMLV2_CACHE_DIR` set to a writable directory and a Python
environment holding rdflib and pySHACL (`spike/ENVIRONMENT.md` lists the versions). M1 to M4 call
the toolkit; M4, M5, and M6 also read the step 4 to 6 artifacts already committed under
`spike/projection/`, `spike/export/`, and `spike/shapes/`. The script writes the full-json exports
(about 1.2 MB each) to `<out-dir>` and the files that back the figures below to
`spike/measurements/`: `m1.json` and `m2.json` (counts, the SHA-256 of every full-json export, and
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
  them, and hands the other 4 or 5 membership ids to different `satisfy` usages. The `satisfy` usages are positional
  because, under `IDS.md`'s id-name rule, a `satisfy` usage takes the name of the requirement it
  references, and the requirement of that name precedes it in the same package; the later claimant
  of a name falls back to a positional segment. `move` shows the rule directly: once `EnclosureRating`
  leaves `PumpSystemModel`, the `satisfy EnclosureRating` usage takes over the requirement's former
  id, which is 1 of the 3 reassigned edited ids.

`insert` shows no untouched churn because no positional element follows either of its insertion
points; an insertion above a positional element behaves like `insert-above-anonymous`. `extract` keeps the id of the usage it retypes (its name is unchanged) and changes the
ids of the body it moves into the new definition; its untouched churn comes from the new
definition's membership, inserted above the `satisfy` usages.

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
`spike/model/pump-library.sysml`; `spike/measurements/m3-roundtrip.sysml` is the output, and
`measure.py` checks that a re-run reproduces it.

Not byte-identical (1915 characters in, 1775 out). The diff is formatting and comments: every `//`
comment is dropped, tabs become four-space indentation, blank lines separating members are removed,
a single-line `@Component { bearer = ...; }` is reformatted across three lines, and
`doc /* The system ... */` loses the space after `/*` (`doc /*The system ...`). No construct, name,
short name, or relationship in the file is lost. `sysmlv2 check --strict --lib <lib>
spike/model/profile.sysml spike/measurements/m3-roundtrip.sysml` exits 0 with no output.

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

No injected row carries a wrong `rdf:type` (`wrong_bearer_type` is a wrong value type), so M6 does
not exercise OQ6's case of a record that arrives with the wrong type.

Step 7 (`spike/holons/BACKENDS.md`) loaded the same shapes as the boundary of a holon over the
normative graph. They validate vacuously there, because their `sh:targetClass`es do not match the
normative graph's class IRIs. Step 7 first ran on holonic `d8d1758`, which predates the
untargeted-node report ([zwelz3/holonic#54](https://github.com/zwelz3/holonic/pull/54)) and
[zwelz3/holonic#56](https://github.com/zwelz3/holonic/pull/56). Re-run on holonic `067f5ea`: the
normative holon reports `conforms = True`, health `intact`, no violations, and 507 untargeted nodes
at Info severity, which is every typed node in its interior. The report now shows the vacuous pass;
at the default Info severity it does not lower the holon's health.

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

`spike/normative/output/pump-system.ttl` (12,068 triples, 507 typed subjects) is regenerated
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

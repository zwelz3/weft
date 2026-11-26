# Open questions

Design questions that are not yet decided. Each entry states the question, what is known, and the current leaning. A question leaves this file when a decision record in `docs/decisions/` settles it.

## OQ1. Reasoning

Reasoning is deferred. OWL reasoning over the exported class layer would detect contradictions that SHACL cannot, for example an element stereotyped as a process whose definition is aligned to a BFO material entity, where BFO declares the two disjoint. Deferring reasoning also defers most of the value of BFO/CCO alignment (OQ4), because without a reasoner or a query that uses the aligned categories the alignment serves as documentation.

Undecided when reasoning becomes a priority is where it runs. The deployed store is Fuseki, where a dataset can be configured with one of Jena's rule-based reasoners (RDFS or an OWL rule set); inferences then stay current, and coverage is limited to what the rule set implements. A DL reasoner run in CI covers more of OWL 2 and produces results only at build time.

## OQ2. Element identity

sysml-toolkit derives each user element's identifier from model structure and names, and documents identifier schemes 2 and 3 with a migration function between them. A rename therefore changes the renamed element's identifier. Decision records, trace links, and the Flexo mirror (decision 0001) all need identifiers that survive edits.

Current leaning, in two parts:

- Every element that the thread links to (requirements, interfaces, components, decisions) carries a declared short name, for example `requirement <'REQ-014'> brakeResponse`. A shape or lint rule enforces this. Weft mints the element's IRI from the short name under a namespace the project controls, and not from the derived identifier or the qualified name, because moving an element changes its qualified name.
- Element-level identity for the mirror is kept in a sidecar map in git (qualified path to UUID), updated by tooling when an element is renamed or moved.

Spike 1 ([spike/RESULTS.md](../spike/RESULTS.md)) measured both parts against toolkit 0.10.2, whose CLI emits only scheme 2. M1: a rename, an insertion among named members, a move within a package, and a reorder change only the edited element's subtree (the rename changed all 29 ids in its subtree and none of the other 478). Adding, removing, or extracting a member above the model's six `satisfy` usages in their package changes every id in those usages (120) and hands 4 or 5 surviving positional ids to different `satisfy` usages. The `satisfy` usages are positional because each takes the name of the requirement it references, and the requirement of that name already holds it in the same package. Moving a requirement to another package hands its id to the `satisfy` usage that references it. A sidecar map keyed by qualified path has no key for a `satisfy` usage, and a map keyed by id cannot detect a reassigned id. M2: two projects that pass the toolkit the same source names share their document root ids, and share every id when the content is identical too; with root-qualified or absolute source names no id is shared, and one project converted from two checkout locations with absolute paths shares no id. The source name Weft passes to the toolkit is therefore part of element identity. Scheme 3 remains unmeasured; spike 2 (next paragraph) found it reachable only through the Rust API.

Spike 2 ([spike/RESULTS.md](../spike/RESULTS.md), step 4) built the toolkit's Python bindings (`sysmlv2-py`) at the same pinned commit and found scheme 3 unreachable from textual notation there too. The bindings expose four `Session` constructors (`from_files`, `from_sources`, `from_interchange_json`, `from_compact_cbor`); the first three build with scheme 2, and `from_compact_cbor` keeps the graph format a payload already names, so it opens a scheme-3 payload but cannot produce one. Neither `Session::from_sources_with_graph_format` (in `sysmlv2-transform`) nor `Model::with_graph_format` (in `sysmlv2-model`), the two Rust-level entry points `IDS.md` documents for scheme 3, is wrapped. At 0.10.2, neither the CLI nor the Python bindings can build a scheme-3 model from text, so M1 and M2 for scheme 3 remain unmeasured until a release adds that wrapper (`spike/ids/test_probe_scheme3.py`, run against that release's checkout, detects one) or until measuring it is worth a Rust harness of its own.

Undecided: whether the sidecar map suffices once thread links to `satisfy` claims are keyed by requirement and satisfying element rather than by toolkit id, or whether the upstream identity issue ([docs/outreach/sysml-toolkit-rename-stable-identity.md](outreach/sysml-toolkit-rename-stable-identity.md)) becomes a blocker; and how Weft fixes the source names it passes to the toolkit.


The 2026-11-26 decision brief (item C1) chose to identify requirements by declared short name (decision 0008), `satisfy` claims by their two ends, and other linked elements through a thin sidecar map; the challenge is tracked in [zwelz3/weft#12](https://github.com/zwelz3/weft/issues/12).

## OQ3. Versions and holons

Each ref (a branch head or a baseline) is a holon whose interior holds that version's normative graph. Element IRIs are stable across version holons, so the IRI identifies the element over its lifetime and the named graph identifies its state at one version. A query that does not scope by graph sees every version's statements at once; thread queries therefore go through a helper that requires a version.

A holon per commit was considered and rejected, because it materializes every commit, which Flexo avoids by materializing only referenced commits. Inferring the latest version from the newest provenance timestamp was rejected, because with more than one branch it selects whichever branch changed last. The current version is a recorded ref.

Two versions cannot share a holon. holonic validates the union of a holon's interior graphs against the union of its boundary graphs, and `traverse()` injects into the first registered interior, so a holon holding two versions would be validated as one merged model.

Open is how a holon's interior refers to a Flexo snapshot when the mirror is in use. A holonic backend that reads through Flexo's per-ref endpoints is the leading option, with holonic's own registry, boundary, and context graphs kept outside the graphs Flexo manages.

## OQ4. Ontology export and reuse

Ontologies are exported from SysML library packages so that a domain definition is reused across models rather than minted again by each one. A library package derives to one ontology with its own namespace and `owl:versionIRI`, and a model that imports the library in SysML derives an ontology that `owl:imports` it. Class IRIs come from the library namespace and the declared name, so two models importing the same library version produce the same class IRIs.

Definitions and specialization derive to OWL classes and `rdfs:subClassOf` without loss. Usages with contextual features, redefinition in context, and feature chains have no direct OWL equivalent, so reusable knowledge belongs in definitions inside library packages. Spike 1 (M4) exported 16 of 16 definitions as classes and 9 of 11 nested typed features as object properties. The two that did not export are scalar-valued (`Real`, `Boolean`), and the spike's exporter emits no `owl:DatatypeProperty`, so they are a gap in the exporter rather than evidence for the limitation above. The spike's library declares no specialization, and its export emits no `owl:Ontology`, `owl:versionIRI`, or `owl:imports`, so the `rdfs:subClassOf` derivation and the per-library ontology with imports are untested on that library. Spike 2's extended library exports 19 of 19 definitions and declares one specialization (`ControllerSensorLink :> DataLink`), for which the export emits one `rdfs:subClassOf` triple; the per-library ontology with imports remains untested.

BFO/CCO grounding is applied through a profile. A stereotype such as `«MaterialArtifact»` is aligned once to its BFO/CCO class in an alignment file kept outside the SysML, and an element that carries the stereotype inherits the alignment in the exported ontology. A test asserts that every alignment row of the stereotype decisions (a stereotype, a `bearer` value, or a row of decision 0006) has exactly one alignment axiom and that every alignment axiom names an existing row. The alignment targets the current CCO release; because CCO publishes new releases, the alignment file records the CCO version IRI it was written against, and a CCO upgrade is a reviewed change to that file.

## OQ5. Identity links and trace links

`owl:sameAs` states that two IRIs denote one individual. It applies to co-reference, such as one pump recorded in an asset database and in a configuration database. It does not apply to a ticket that tracks a requirement or a commit that implements one; those are trace links and use the OSLC link vocabulary.

Fuseki merges nothing on `owl:sameAs` unless a reasoner that implements the equality rules is configured for the dataset, so with the deployed store an identity assertion changes query results only where a query or portal follows it explicitly.

Current leaning is a holon subtype that holds only identity assertions, each with provenance naming the matcher or person that made it. Queries and portals can include or exclude that graph, and a wrong match is withdrawn by removing it from one graph. This requires a holonic enhancement; holonic's `AlignmentHolon` holds vocabulary mappings and is not extended to entity identity.

## OQ6. Derived shapes for instance data

SHACL shapes generated from definitions (`sh:datatype` and `sh:class` from typing, cardinality from multiplicity) would validate records in other systems against the model. A shape that targets a class reports conformance when no instance of that class is present, so records that arrive with the wrong type pass without a finding. holonic resolved this (holonic OQ11, distinct from Weft's OQ11 below) in [zwelz3/holonic#54](https://github.com/zwelz3/holonic/pull/54), together with [#30](https://github.com/zwelz3/holonic/issues/30), in which results with an unrecognized severity were dropped. Membrane validation now reports each typed node that no boundary shape targets: at Info by default, and as a violation for the nodes a `traverse(fail_on_breach=True)` injects. A holon's boundary can exempt a class with `cga:permitsType` or set the severity with `cga:untargetedTypeSeverity`.

Open is which of those settings Weft's source holons use. A portal that carries instance records into a model holon with `fail_on_breach` rejects records whose types the derived shapes do not target, which is the intended behavior for mistyped rows; auxiliary nodes the adapter emits (measurement or provenance nodes, for example) then need shapes or `cga:permitsType` declarations. Spike 1 step 6 (M6) found a result on the faulty property for each of 10 injected faults on a stand-in instance table. The same shapes flagged 10 of the 18 clean rows, because the derivation requires exactly one value for every port and interface feature and the table has no columns for them. No injected row had a wrong `rdf:type`, so the spike did not test the mistyped-record case above. The adopter's table from issue #1 repeats the step. Step 7 found a second gap: the derived shapes target the exported class IRIs, so as a boundary over the normative graph, which is typed with the toolkit's metaclass IRIs, they validate vacuously. On holonic `067f5ea` that membrane lists all 507 typed nodes of spike 1's graph as untargeted at Info with health intact, and reports health compromised when the boundary sets `cga:untargetedTypeSeverity sh:Violation`. A boundary for the normative graph needs shapes stated over the toolkit's class IRIs, a separate derivation. The fixes are on holonic `main` and are not in a release; holonic 0.8.0 on PyPI does not have them.

Spike 2 (step 2) hand-wrote three profile shapes over the toolkit's class IRIs (`spike/shapes/normative-shapes.ttl`), targeting `sysml:MetadataUsage`, `sysml:AttributeUsage`, and `sysml:InterfaceDefinition`, and showed that each has a focus node on the pump-system normative graph that satisfies its SPARQL precondition and that each fires on a deliberately malformed node. That makes those three shapes non-vacuous on the raw graph; it does not close the boundary gap. Loaded as the normative holon's boundary, the file leaves 612 of the extended graph's 630 typed subjects untargeted. Spike 2 (step 1) found the same detection as spike 1's step 7 re-run on the extended graph, on both the rdflib and Fuseki backends: `MembraneResult.untargeted` lists all 630 typed subjects, and with `cga:untargetedTypeSeverity sh:Violation` declared in the boundary the membrane reports `conforms = True` and health compromised. On the step 6 shapes regenerated from spike 2's extended model, M6 finds a result on the faulty property for 8 of the 10 injected faults; the two rows it misses carry two distinct `bearer` values, which decision 0005 allows, so they are no longer faults. Open, in addition to the settings question above, is whether a normative-graph boundary covers the toolkit's other metaclasses with shapes or exempts them with `cga:permitsType`. The shapes read the toolkit's FeatureValue expression trees through a property path rather than a flattened property, because that is the shape raw toolkit-AST data takes; a generator that derives such shapes from a definition's declared structure would need to walk the same expression tree, not only swap which class IRI it targets. A derivation covering the other stereotypes, beyond Component and Interface, remains open.

## OQ7. Flexo's RDF representation

flexo-mms-sysmlv2 (at `61d1c9da77e1f0eebd4734290b8bb04fb04162f0`) maps API JSON to RDF key by key. Element IRIs are `urn:sysmlv2:element:<id>` on every deployment, each element carries only its most specific metaclass, multi-valued properties keep their order only in a serialized JSON string, and a JSON `null` is stored as `rdf:nil`. Round trips through the API are unaffected. The issues limit direct SPARQL consumers, and a report to the Flexo maintainers is drafted but not filed.

## OQ8. Behavioral execution

Out of scope at the start. OpenSysML is the only implementation that executes actions and state machines, and its state machines accept constructs outside the SysML v2 grammar (`initial`, `region`, `history`, `choice`, `junction`, `defer`), so a model that uses them is specific to OpenSysML. The first use case that would justify execution is verification, for example running an interface protocol modeled as a state machine against recorded traffic.

## OQ9. Round trip for edits made in Flexo

Tier 2 in decision 0001 depends on converting SysML v2 API JSON back to textual notation. sysml-toolkit reads JSON back to text. Spike 1 (M3) measured the loss on toolkit 0.10.2: every `//` comment is dropped and indentation, blank lines, and single-line bodies are reformatted. No construct, name, short name, or relationship is lost. Tier 2 therefore needs comment preservation, either upstream or by keeping comments in `doc` elements.

## OQ10. Projection vocabulary and adapter ontologies

The digital thread has no central ontology. Each adapter (Excel, Teamwork Cloud, and others) maps its source into its own ontology, and linking across them is unfinished. The projection's terms (component, interface, requirement, decision, and the trace links between them) are therefore Weft's own vocabulary rather than an alignment to an existing one. Open is whether adapter ontologies align to the projection through holonic alignment holons, which makes the projection the hub for cross-source queries, or whether each pair of sources is aligned directly. The first needs one alignment per adapter; the second needs one per pair of adapters that must be queried together. Spike 1 (M5) expressed each of the five thread queries against the projection, in three to six triple patterns by spike 2's count.

Spike 2 (step 3) wrote the normative-graph equivalent of all five queries and measured the saving directly. Against the full normative graph, three queries needed more triple patterns (3, 4, and 6 more, for the usage-to-definition and verification-membership walks the projection flattens), one needed the same number, and one needed one fewer, because the projection's verdict pattern has no graph counterpart. None needed a property-path operator on this model (630 typed elements). Run times were not measured with enough repetition to compare the two graphs. The saving the projection buys on this model is a small, fixed number of joins per query, not an asymptotic one; whether it stays fixed on a model with deeper nesting (more components per system, more metadata layers) is unmeasured.

## OQ11. Graphical editing and tier 2

Decision 0001 places edits made in tools that write to Flexo (tier 2) out of plan, and the initial adopter needs graphical editing ([docs/plans/adopter-capabilities.md](plans/adopter-capabilities.md), C2). The adopter's editor is Starforge Kotar, whose public support repository describes a browser workspace that commits to GitLab through git smart-HTTP and shows, in a draft architecture diagram, a source-control component writing to a textual model repository with Flexo optional.

Current leaning is that Kotar's graphical edits reach git as changes to textual notation, which makes graphical editing a tier 0 feature for this adopter and leaves tier 2 out of plan. The leaning rests on documentation, not on a model edited in Kotar. Three points remain to verify with a model edited graphically in Kotar:

- whether an edit rewrites only the changed elements or regenerates the file, which decides the size of review diffs;
- whether the output stays within the SysML v2 grammar that sysml-toolkit checks (decision 0002);
- whether declared short names (OQ2) and metadata annotations, including Weft's trace metadata, survive an edit.

A tool that keeps its own store and does not commit text would still need tier 2, so the question stays open for other adopters.


The check is assigned to the adopter in [zwelz3/weft#13](https://github.com/zwelz3/weft/issues/13), blocked on the Kotar container release.

## OQ12. Links from requirements to source passages

Deferred. The initial adopter supplies requirement text in the prompt to the agent, and under AGENTS.md rule 2 the prompt is not a record, so a requirement's provenance is the commit that added it and the review that approved it.

For an adopter whose requirements come from documents or from a requirements tool, a requirement needs a link to the passage it came from, and the profile brief's trace metadata has no feature for it. Three ranges are candidates, and each is a different graph contract:

- a document IRI with a fragment identifier, emitted under `dct:source`;
- a passage resource with its own IRI, linked by `prov:wasDerivedFrom`, carrying the document, its revision, and the location within it;
- a link to an element in a requirements-tool export (ReqIF), when the source is a requirements tool rather than a document.

The leaning, when the question is taken up, is the passage resource, because it records the document revision, so a later revision of the document can be compared with the requirements derived from the earlier one.

## OQ13. Issue state in reports

The profile brief stores issue keys in the model and resolves them to IRIs, which supports a traceability matrix that lists keys. Reports that use an issue's state (status, resolution, assignee) need data held in Jira or GitLab. Decision 0001 requires the core to work without a server, and AGENTS.md rule 9 forbids network access at validation time. The initial adopter records links only, so Weft reads issue systems and never writes to them; creating issues is a candidate agent tool for other adopters.

Current leaning is an adapter per issue system that runs as its own step, in CI or on demand, and writes issue state into a source holon with the time of synchronization in its context graph. Validation and report generation read only that holon, and a report states the synchronization time it reflects. Open is whether the synchronized state is committed to git or kept as a build artifact; committing it makes reports reproducible from a checkout, and keeping it as an artifact keeps issue data out of the model's history.

## OQ14. Flexo, Kotar, and the long-term architecture

Decision 0001 makes git the record and Flexo MMS an optional one-way mirror (tier 1). The adopter edits in Starforge Kotar, whose support repository describes a browser workspace that commits textual notation to GitLab, with a remote Flexo marked optional (OQ11). Kotar therefore offers a second path from tools to git that does not pass through Flexo, and the two paths imply different long-term architectures. In one, Flexo is the shared query and integration layer that tools write through; in the other, git stays the only integration point and Flexo is a read mirror at most.

Open is which architecture Weft commits to, and what that means for tier 1 and tier 2 in decision 0001. Two drafted upstream reports wait on the answer and are recorded as to be filed: [docs/outreach/flexo-sysmlv2-rdf.md](outreach/flexo-sysmlv2-rdf.md) and [docs/outreach/sysml-toolkit-rename-stable-identity.md](outreach/sysml-toolkit-rename-stable-identity.md). The second gains the identity evidence in [zwelz3/weft#12](https://github.com/zwelz3/weft/issues/12) before it is filed.

## OQ15. Versioning of the projection vocabulary

Spike 1's projection terms live under a namespace that contains the contract version (`thread/0.1.0/`), so every contract version renames every term, which is a data migration for every user (AGENTS.md rule 3). `proj:satisfiedBy` is declared with range `proj:Component`, while SysML lets any feature satisfy a requirement, and the spike's model already has satisfiers that are not components.

Current leaning, chosen in the 2026-11-26 decision brief: an unversioned namespace whose ontology carries `owl:versionIRI`, and `proj:Element` as the range of `proj:satisfiedBy`. The question stays open because it blocks the 1.0 release ([docs/plans/release-1.0.md](plans/release-1.0.md)), and the namespace's domain depends on decision 0009's open choice of a domain for Weft's own vocabulary.

## OQ16. Properties whose JSON key holds both references and literals

The toolkit's JSON uses one key for different relations in different metaclasses; `value` holds a reference to an expression in a `FeatureValue` and a literal in a `LiteralString` or `LiteralInteger`. Spike 1's contract emitted one IRI, `tk:value`, as both an object property and a datatype property. OWL 2 keeps the two property kinds disjoint, and the OWL API reports the overlap as illegal punning ([IllegalPunning.java](https://github.com/owlcs/owlapi/blob/version5/api/src/main/java/org/semanticweb/owlapi/profiles/violations/IllegalPunning.java)); a rule-based reasoner such as owlrl 7.6.2 accepts it silently, so only DL tooling catches the problem.

Practice in established vocabularies, surveyed for the 2026-11-26 decision brief (item C3):

- Vocabularies that stay within OWL DL split one concept into a named object property and a named datatype property: SOSA's `hasResult` and `hasSimpleResult`, Wikibase's `ps:` and `psv:` predicates, and OBI's `has value specification` (OBI_0001938) and `has specified value` (OBI_0002135).
- Vocabularies that keep a single untyped property give up OWL DL and enforce ranges elsewhere: QUDT's `qudt:value` is an `rdf:Property` constrained per class in SHACL, and OMG's SysML v2 API JSON-LD contexts map `value` to one term, `@id`-typed for `FeatureValue` and literal-typed for the literal metaclasses.
- schema.org declares `Text` a class and every mixed property an object property, which its own documentation calls an approximation.
- No surveyed vocabulary uses one IRI per (metaclass, property) pair.

Current leaning, chosen in the decision brief and supported by the survey: split each mixed key by range kind into one object property and one datatype property, named `valueRef` and `valueLiteral` for `value` and by the same pattern for any other mixed key. Marking both names, rather than keeping a bare `value` for the literal as OBI and PROV do, avoids silently narrowing the meaning of the draft's `tk:value` for anyone who authored against it. The question stays open because property IRIs are part of the contract that 1.0 fixes ([docs/plans/release-1.0.md](plans/release-1.0.md)) and because it is on the ontologist's review list.

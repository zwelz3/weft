# 0008. Requirement as a prescriptive information content entity, identified by its declared short name

- Status: accepted (2026-11-26)
- Date: 2026-11-26

## Context

The profile brief ([docs/plans/profile-brief.md](../plans/profile-brief.md)) lists Requirement as a minimum stereotype for `requirement def` and `requirement`, with "statements of what a system must do or be" as the instances of the exported class and the CCO directive information content entity as the candidate alignment. Three points are open: what an instance of the exported class is, whether the stereotype needs a metadata tag, and which elements the thread links to.

SysML v2 gives a requirement definition different instances. The standard library documents `Requirements::RequirementCheck` as the base type of all requirement definitions, and it specializes `ConstraintCheck`, `BooleanEvaluation`, `Evaluation`, and `Performance`. An instance of a requirement definition is therefore one evaluation of the requirement's constraints against a subject, an occurrence that in BFO falls under [process](http://purl.obolibrary.org/obo/BFO_0000015). A ticket, a commit, or a test does not concern one such evaluation. It concerns the requirement as stated, such as SYS-001 with its text, and the same statement holds for every subject it is checked against.

The class the brief names is [CCO `ont00000965`](https://www.commoncoreontologies.org/ont00000965), whose current label is "Prescriptive Information Content Entity" ("Directive ICE" survives as an alternative label) in the CCO release with version IRI `https://www.commoncoreontologies.org/2026-08-13/CommonCoreOntologiesMerged`. Its definition is "An Information Content Entity that prescribes some Entity", and its subclasses include Quality Specification (`ont00000575`), Performance Specification (`ont00000127`), and Process Regulation (`ont00001324`), the parent of Process Requirement (`ont00001224`).

Decision 0006 ruled that Weft adds no metadata tag where SysML notation already marks the distinction, because a tag duplicates the notation and the toolkit does not check that the two agree. A requirement's metaclass already marks it as a requirement. The Component stereotype (decision 0005) needs a tag because `part def` does not say whether a part is a component.

## Decision

The Requirement stereotype applies to `RequirementDefinition` and `RequirementUsage` elements, which includes `concern def` and `concern` because SysML specializes them from requirements. It does not apply to `SatisfyRequirementUsage` (a `satisfy` claim), which the derivation exports as a claim between a requirement and its satisfying element. Weft adds no metadata tag; the metaclass is the stereotype.

| Element | Instances of the exported class | Alignment |
|---|---|---|
| `requirement def` | Requirement statements of the kind the definition describes | Subclass of the profile's Requirement class, which is a subclass of [CCO Prescriptive Information Content Entity](https://www.commoncoreontologies.org/ont00000965) |
| `requirement` usage with a declared short name | None. The usage is one requirement statement | A named individual of its definition's exported class, or of the profile's Requirement class when it has no user definition |
| `requirement` usage without a declared short name | None | The same as a usage with a short name, identified by the toolkit's derived identifier instead. The Violation shape below keeps thread links off it |

This departs from SysML's semantics on purpose. The exported class describes the statement that tickets, commits, and tests refer to, and the evaluations SysML defines are what `sysmlv2 verify` reports on, so the derivation records each verdict on its `satisfy` claim rather than as an instance of the requirement class.

A project aligns its own requirement definitions to a narrower CCO class in its own alignment file, for example a mass limit to Mass Specification (`ont00000693`), with the axiom minted under the project's namespace (AGENTS.md rule 4). The profile does not require it, because one requirement definition can prescribe a quality, a performance, and a process at once.

The declared short name is the requirement's identity in the thread. The graph contract mints the requirement's IRI from it under the project's namespace (OQ2). Two SHACL shapes apply:

- At Violation severity, a requirement usage that is the target of a `satisfy` claim, a `verify` in a verification objective, a derivation connection, a refinement, or a trace metadata link has a declared short name. Without it the link would point at an identifier derived from the model's structure and names, which a rename changes. The short name is written in textual notation, so the shape is satisfiable through the primary authoring path (AGENTS.md rule 7).
- At Warning severity, a requirement usage with a declared short name has documentation text (a `doc` comment). A requirement may be stated only as a constraint, so the text is a production-readiness signal rather than a rule.

The derivation does not relate a requirement to its subject with CCO's `prescribes` (`ont00001942`) in this decision. `prescribes` relates a prescriptive information content entity to an entity, and a requirement's `subject` is a typed feature, not an individual. The subject relation is emitted under a property fixed in [docs/graph-contract.md](../graph-contract.md).

The following textual notation passes `sysmlv2 check --strict` with sysml-toolkit 0.10.2. `SYS-001` and `SYS-002` are thread requirements. `motorShare` is part of `SYS-001`'s statement, and the requirement usage that `verify pumpMass` creates in the objective has no short name, so it is exported as the verification link and not as a requirement.

```sysml
package Plant {
    private import ISQ::*;
    private import SI::*;
    private import RequirementDerivation::*;
    part def Pump { attribute mass : MassValue; }
    requirement def MassLimit {
        subject p : Pump;
        attribute limit : MassValue;
        require constraint { p.mass <= limit }
    }
    requirement <'SYS-001'> pumpMass : MassLimit {
        doc /* The pump shall have a mass of no more than 40 kg. */
        attribute :>> limit = 40 [kg];
        requirement motorShare {
            doc /* The motor's share of the mass budget is tracked separately. */
        }
    }
    requirement <'SYS-002'> motorMass : MassLimit {
        doc /* The motor shall have a mass of no more than 25 kg. */
        attribute :>> limit = 25 [kg];
    }
    #derivation connection {
        end #original ::> pumpMass;
        end #derive ::> motorMass;
    }
    concern def Portability;
    part pump1 : Pump { attribute :>> mass = 38 [kg]; }
    satisfy pumpMass by pump1;
    verification def MassTest {
        subject testPump : Pump;
        objective { verify pumpMass; }
    }
}
```

## Consequences

Every requirement in a model is classified without authoring effort, and only the ones the thread links to need a short name. A model written in Kotar or by an agent needs no Weft metadata on its requirements, so OQ11's third point (whether short names and metadata survive an edit in Kotar) reduces to short names for this stereotype.

The graph contract's minting rule (a requirement element with a declared short name mints `{base}requirement/{short_name}`) stays as drafted in spike 1, and the Violation shape above makes it total for every requirement the thread links to.

A `satisfy` claim is usually anonymous, and the toolkit derives an anonymous element's identifier from its position. Re-running spike 1's model with sysml-toolkit 0.10.2 changed 120 identifiers inside the model's `satisfy` claims when one part definition and one part were inserted above them, while the requirements' short names were unaffected. The graph contract therefore identifies a claim by its requirement's IRI and its satisfying element's IRI rather than by the toolkit's identifier for the claim.

Concerns export as requirements, because SysML specializes them from requirements.

A user story is a requirement or a concern with a `stakeholder` member naming the persona it serves. The adopter's maturity measures are requirement-centric, so stories then appear in the traceability matrix and the gap analysis with no further mapping, and stakeholder coverage is one query over requirements. A use case with an actor remains available for behavior and links to its stories through its objective.

No metadata tag for identity is needed beyond the declared short name. A short name is SysML notation and is unchanged by a rename of the declared name or a move to another package, so an IRI minted from it under the project's namespace survives both; spike 1's re-run shows the derived identifiers of named requirements change under a move. Claims are identified by their two ends, as above, and elements the thread does not link to need no stable identity.

The alignment file declares the profile's Requirement class under the profile's namespace with one axiom to `ont00000965`, and records the CCO version IRI above. Decision 0006 and the profile brief call `ont00000965` the directive information content entity; the IRI is the same, and the documentation uses the current label when the alignment file is written.

A test asserts that the corpus model contains a requirement definition, a requirement usage with a short name that is the target of each link kind in the Violation shape, and a nested requirement without a short name (AGENTS.md rule 8).

## Alternatives considered

A `#Requirement` metadata tag whose definition restricts `annotatedElement` to `RequirementDefinition` and `RequirementUsage`. sysml-toolkit 0.10.2 enforces the restriction (`validateMetadataFeatureAnnotatedElement` rejects the tag on a `part def`) but accepts it on a `satisfy` claim, because `SatisfyRequirementUsage` specializes `RequirementUsage`, so excluding claims would take a Weft shape as well. Rejected because it duplicates the metaclass (decision 0006's reasoning), adds a piece of Weft metadata that every editing tool must preserve, and lets a requirement exist without the tag, which would leave it out of the thread silently.

Requirement usages exported as classes, as part usages are (OQ4). Rejected because tickets and tests refer to one statement, and a link attached to a class says something about every member of it.

Instances as requirement checks, following SysML's semantics, aligned to BFO process. Rejected because no trace link concerns one evaluation, and the verdicts that do concern evaluations are recorded on `satisfy` claims.

A narrower CCO class for every requirement, such as Quality Specification. Rejected because requirement kinds vary within one model and one requirement can prescribe more than one kind of entity.

A short name required on every requirement usage at Violation severity. Rejected because nested anonymous requirements and verification objectives are ordinary SysML and the thread does not link to them.

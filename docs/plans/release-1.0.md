# Release 1.0 gates

Weft's 1.0 release fixes the graph contract (AGENTS.md rule 3), after which a change to emitted IRIs or triples is a migration for every user. This plan lists what has to be settled before that release. An item leaves the list when its record is updated, not when this file is edited.

## Open questions that block 1.0

| Question | Leaning | Blocking because |
|---|---|---|
| [OQ15](../OPEN-QUESTIONS.md) Versioning of the projection vocabulary | Unversioned namespace with `owl:versionIRI`; `proj:satisfiedBy` ranges over `proj:Element` | Projection IRIs are part of the contract |
| [OQ16](../OPEN-QUESTIONS.md) Properties whose JSON key holds both references and literals | Split each mixed key into an object property and a datatype property (`valueRef`, `valueLiteral`) | Property IRIs and ranges are part of the contract |
| Domain of Weft's own vocabulary (decision 0009) | A w3id.org redirect | Profile and projection IRIs are minted under it |

## Ontology design decisions for review by an ontologist

Each decision below fixes what an exported class or property means, so each is reviewed by an ontologist before 1.0 and the outcome is recorded in the decision itself.

| Record | Ontology choice to review |
|---|---|
| [Decision 0005](../decisions/0005-component-stereotype.md) | Component as a BFO role; the open `bearer` list; the information bearer's path through concretization and inherence |
| [Decision 0006](../decisions/0006-interface-stereotype.md) | Interface definitions as prescriptive information content entities; `individual` definitions as material entities linked to their specification by an object property whose value is the specification's IRI used as an individual (OWL 2 punning), with no `rdfs:subClassOf` across the two |
| [Decision 0007](../decisions/0007-action-definition-stereotype.md) | `action def` as BFO process rather than CCO function |
| [Decision 0008](../decisions/0008-requirement-stereotype.md) | Requirement statements as prescriptive information content entities rather than SysML's requirement checks; requirement usages with short names as named individuals |
| [Decision 0009](../decisions/0009-iri-bases.md) | IRI bases per project and per library package; OMG identifiers for the standard library |
| [OQ4](../OPEN-QUESTIONS.md) | Definitions as OWL classes, specialization as `rdfs:subClassOf`, usages as restrictions on their owner's class |
| Attribute definitions as OWL classes (chosen in the 2026-11-26 decision brief, item C5; implemented in spike 2's exporter) | Value kinds such as `BearerKind` exported as classes whose values are individuals, which decision 0005's per-value alignment axioms need |
| [OQ15](../OPEN-QUESTIONS.md) and [OQ16](../OPEN-QUESTIONS.md) | As above |

## Other gates

Every acceptance criterion in the [profile brief](profile-brief.md) passes, and [docs/graph-contract.md](../graph-contract.md) is no longer a draft.

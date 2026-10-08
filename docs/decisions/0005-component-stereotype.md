# 0005. Component as a role borne by a material artifact or carried by information

- Status: accepted (revised 2026-10-08: open `bearer` list)
- Date: 2026-10-08

## Context

The profile brief ([docs/plans/profile-brief.md](../plans/profile-brief.md)) lists Component as a minimum stereotype for `part def` and `part`, and leaves its alignment open. A hardware component is a material artifact in CCO, and a software component is an information content entity. A stereotype aligned to either class excludes the other kind of component.

Being a component is not what a thing is. A pump is a material artifact whether or not it is installed in the system under design, and it is a component of that system only while it plays that part. BFO represents a part an entity plays, which it can lose without ceasing to exist, as a role ([BFO role](http://purl.obolibrary.org/obo/BFO_0000023)).

BFO 2020 restricts what can bear a role. A role is a specifically dependent continuant and inheres only in an independent continuant. An information content entity is a generically dependent continuant ([BFO generically dependent continuant](http://purl.obolibrary.org/obo/BFO_0000031)), so it cannot bear a role directly. A software component bears its role through the material entity that concretizes it, such as the storage on which a build artifact is deployed.

The buildability review ([docs/reviews/2026-10-08-buildability.md](../reviews/2026-10-08-buildability.md)) proposed this framing.

## Decision

The Component stereotype applies to `part def` and `part`. It aligns to a component role, a subclass of [BFO role](http://purl.obolibrary.org/obo/BFO_0000023) that the profile alignment file declares under the profile's namespace. The hardware-versus-software distinction moves from the stereotype to its bearer.

The stereotype requires one metadata feature, `bearer`, with multiplicity `[1..*]`. Its type is the attribute definition `BearerKind`, and its values are attribute usages of that type. The profile declares two values.

| `bearer` | Instances of the exported class | Alignment axioms |
|---|---|---|
| `material` | Physical objects that bear the component role | Subclass of [CCO material artifact](https://www.commoncoreontologies.org/ont00000995), and of [bearer of](http://purl.obolibrary.org/obo/BFO_0000196) some component role |
| `information` | Information content entities, such as a software module, whose concretizations bear the component role | Subclass of [CCO information content entity](https://www.commoncoreontologies.org/ont00000958), and of [is concretized by](http://purl.obolibrary.org/obo/BFO_0000058) some entity that is [bearer of](http://purl.obolibrary.org/obo/BFO_0000196) some component role |

The list is open. A project adds a value by declaring an attribute usage of type `BearerKind` in its own package, and adds one alignment axiom for it to its own alignment file. The value and its axiom are minted under the project's namespace (AGENTS.md rule 4). The list is not an enumeration, because sysml-toolkit 0.10.2 rejects an enumeration that specializes another (`validateDefinitionVariationSpecialization`), so an enumeration could not be extended outside the profile.

An element with more than one value gets the alignment axioms of each value. Firmware shipped on a chip is one element with `bearer = (material, information)`.

A SHACL shape requires at least one `bearer` value at Violation severity, and a second shape requires every value to have exactly one alignment axiom. The value is written in textual notation on the metadata usage, so the shape is satisfiable through the primary authoring path (AGENTS.md rule 7). An element carrying the stereotype requires a declared short name, because the thread links to components (OQ2).

The following textual notation passes `sysmlv2 check` with sysml-toolkit 0.10.2.

```sysml
package WeftProfile {
  attribute def BearerKind;
  attribute material : BearerKind;
  attribute information : BearerKind;
  metadata def Component { attribute bearer : BearerKind[1..*]; }
}
package Plant {
  private import WeftProfile::*;
  attribute firmware : BearerKind;
  part def Controller { @Component { bearer = (material, information); } }
  part def BootLoader { @Component { bearer = firmware; } }
}
```

## Consequences

One stereotype covers hardware and software, and a query for all components of a system needs no union over two stereotypes.

A query for all components of one bearer kind matches on the `bearer` value, and a project value without an alignment axiom fails validation instead of exporting an unaligned class.

The alignment file declares the component role class under the profile's namespace, so the IRI is minted into a namespace Weft controls (AGENTS.md rule 4). The CCO IRIs above are confirmed against the CCO release recorded in the alignment file before that file is written.

The Material artifact stereotype in the profile brief remains for parts that are not components of the system under design, such as test equipment and tooling.

## Alternatives considered

A closed `bearer` enumeration of `material` and `information`, with firmware modeled as two elements joined by a composition. This was the first version of this decision. Rejected in review because a project with another kind of bearer had no way to add it, and because splitting one physical part into two elements to satisfy the profile misrepresents the model.

A different CCO class as a common parent for hardware and software components. Rejected because CCO places material artifacts under BFO material entity and information content entities under BFO generically dependent continuant, and the nearest common parent is BFO continuant, which carries no component semantics. The role already provides the common class.

Two stereotypes, Hardware component and Software component. Rejected because the distinction concerns the bearer and not the role, and because every component query would need both.

Component aligned directly to CCO material artifact, with software left to a separate stereotype. Rejected because it encodes the hardware case as the default and gives software components no component semantics.

An information content entity bearing the role directly. Rejected because BFO 2020 does not allow a generically dependent continuant to bear a specifically dependent continuant.

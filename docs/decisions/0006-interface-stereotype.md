# 0006. Interface specifications and realized connections, separated by the SysML individual keyword

- Status: accepted (revised 2026-10-08: usages and instances are stereotyped)
- Date: 2026-10-08

## Context

The profile brief ([docs/plans/profile-brief.md](../plans/profile-brief.md)) lists Interface as a minimum stereotype for `interface def` and `port def`, and leaves open what an instance of the exported class is. Two readings fall in different BFO categories. The specification of an interaction, such as the signals, protocol, and connector a port must provide, is an information content entity. A realized connection, such as a cable installed between two pumps in one plant, is a material entity or a relational quality between two material entities.

The first version of this decision applied the stereotype to definitions only and left realized connections to adapter data. Review rejected that because it leaves a model with no way to type a specific installed connection, even when the model records one.

SysML v2 already marks the distinction. The `individual` keyword on an occurrence definition declares a definition with exactly one instance, and an `individual` usage must be typed by one individual definition. `interface def` and `port def` are occurrence definitions, so the keyword applies to both. sysml-toolkit 0.10.2 enforces the typing rule (`validateOccurrenceUsageIndividualUsage`).

## Decision

The Interface stereotype applies to `interface def`, `port def`, `interface`, and `port`. The `individual` keyword on the stereotyped element selects what the element exports.

| Element | Instances of the exported class | Alignment |
|---|---|---|
| `interface def` or `port def` without `individual` | Interface specifications | Subclass of [CCO directive information content entity](https://www.commoncoreontologies.org/ont00000965) |
| `interface` or `port` usage without `individual` | None. The usage is a feature of its owning definition | Exported as a restriction on the owner's class that requires a feature conforming to the usage's definition |
| `individual interface def` or `individual port def` | The one realized connection or port it names | A named individual typed as a realized interface, a subclass of [BFO material entity](http://purl.obolibrary.org/obo/BFO_0000040) declared under the profile's namespace |
| `individual interface` or `individual port` usage | The same individual, in the context of its owner | The usage's individual, related to its owner's individual |

An individual definition specializes the specification it realizes, as in `individual interface def CableC7 :> FluidLink`. The derivation emits that specialization as an object property from the individual to the exported specification class, whose range is the specification class (AGENTS.md rule 5). The property's name and namespace are fixed in [docs/graph-contract.md](../graph-contract.md). Records of installed connections held in an adapter holon, such as rows of a cabling workbook, use the same property.

Weft adds no instance metadata tag. The `individual` keyword is the tag, and the toolkit checks its well-formedness (AGENTS.md rule 6).

An element carrying the stereotype requires a declared short name (OQ2).

The following textual notation passes `sysmlv2 check` with sysml-toolkit 0.10.2.

```sysml
package Plant {
  port def FluidPort;
  interface def FluidLink { end a : FluidPort; end b : FluidPort; }
  individual interface def CableC7 :> FluidLink;
  individual interface cableC7 : CableC7;
}
```

## Consequences

Specifications and realized connections export to different BFO categories, and the `individual` keyword decides which one, so no element needs a case split in its alignment.

A model that records specific installations types them directly, and the same link property relates a modeled installation and an adapter record to their specification. A query for every realization of `FluidLink` returns both.

The realized-interface class is minted under the profile's namespace (AGENTS.md rule 4). The CCO IRIs above are confirmed against the CCO release recorded in the alignment file before that file is written.

A test asserts that the corpus model contains a stereotyped element of each row in the table (AGENTS.md rule 8).

## Alternatives considered

The stereotype on definitions only, with realized connections left to adapter data. This was the first version of this decision. Rejected in review because a model that records an installed connection could not type it.

A Weft metadata tag marking an element as an instance. Rejected because it duplicates the SysML `individual` keyword, and the toolkit would not check that a tagged usage is typed by a tagged definition.

Two stereotypes, Interface specification and Interface connection. Rejected because the `individual` keyword already separates the two, and a second stereotype would allow the two markings to disagree.

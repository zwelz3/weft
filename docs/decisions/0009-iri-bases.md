# 0009. OMG identifiers for the standard library and a configured IRI base per project and per library package

- Status: accepted
- Date: 2026-11-26

## Context

AGENTS.md rule 4 allows IRIs to be minted only into namespaces their owner controls. Spike 1's draft graph contract ([docs/graph-contract.md](../graph-contract.md)) minted three kinds of element under one base, `weft.ghostsystems.ai/spike1/...`: the project's own elements, the classes of the project's library packages, and references to elements of the OMG standard library. No decision establishes that domain as one Weft controls, and ghostsystems.ai is the domain of a contributor's organization.

The three kinds have different owners. A project's elements belong to the project. A library package belongs to whoever publishes it, and open question OQ4 requires one ontology namespace per library package so that two models importing the same library version produce the same class IRIs. Standard-library elements belong to OMG, and sysml-toolkit resolves each of them to its normative element identifier from the published KerML and SysML libraries (decision 0002).

## Decision

| Element | IRI base |
|---|---|
| An element of the OMG standard library | OMG's normative element identifier, as the toolkit resolves it; Weft mints no IRI for it |
| A class or property exported from a library package | The base configured for that library package |
| Any other element of a project | The base configured for the project |

Bases are configured per project, in the project's Weft configuration, and per library package, in the configuration shipped with the package. Weft has no default base, so a project or library package without one fails derivation with an error that names the missing setting. Weft's own vocabulary (the profile and the projection terms) is the only namespace Weft itself mints into, and its domain is fixed in the profile work.

## Consequences

The graph contract's minting rule changes from one base to the three rows above; spike 1's `spike/namespace.toml` is replaced by per-project and per-library settings when the derivation is written.

A thread link to a standard-library element uses OMG's identifier, so two projects that reference `ScalarValues::Real` link to the same IRI.

The domain of Weft's own vocabulary is an open choice (a w3id.org redirect is the usual option); until it is made, the profile and projection namespaces stay drafts.

## Alternatives considered

Confirming weft.ghostsystems.ai as Weft's domain for every element. Rejected because it mints a project's and a library's elements into a namespace neither controls, which rule 4 forbids.

A Weft-controlled domain for every element. Rejected for the same reason: Weft would own IRIs for data that belongs to its users.

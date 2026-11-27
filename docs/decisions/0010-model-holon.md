# 0010. A model holon aggregates the holons of its versions

- Status: proposed
- Date: 2026-11-27

## Context

Decision 0003 makes each model version a holon, and OQ3 makes each ref (a branch head or a baseline) such a version holon. Element IRIs are the same in every version holon, so an IRI identifies an element over its lifetime and a holon identifies the element's state at one ref. Decision 0003 lists model membership in each version holon's context layer but names no holon that stands for the model. A consumer that needs the model as it currently stands (an adapter's portal, a report, a link from an issue tracker) therefore addresses a version holon, and the holon it must address changes whenever the current ref changes.

holonic expresses containment with `cga:memberOf`, from a child holon to its parent. Its shapes report a holon with more than one parent at Info severity. `resolve(..., order="containment")` walks containment in both directions. Membrane validation does not follow it; `validate_membrane` validates a holon's own interior graphs against its own boundary graphs, with no contribution from parent or children. holonic defines `cga:AggregateHolon` as a holon with no original data, whose interiors are populated entirely by portal traversals.

A probe on holonic `067f5ea` (the pin in decision 0003) placed two version holons under an aggregate holon and found five behaviors this design depends on:

- A boundary graph registered on several holons, by passing its IRI to `add_boundary`, validates each of them.
- A traversal adds to the target's interior. After traversals from both versions, the aggregate held both versions' values of one attribute, and its membrane failed a `sh:maxCount 1` shape.
- `rollback_traversal` removes the triples a traversal injected, matched by content. Rolling back the first version's traversal after the second's also removed a triple that both versions carry unchanged.
- `derivation_chain` still lists a source after its traversal is rolled back.
- `traverse` records a provenance activity only when it is given `agent_iri`.

holonic has no operation that unregisters one layer of a holon. `remove_holon` removes the holon and detaches its children, which then have no parent.

## Decision

Each model has one model holon, typed `cga:AggregateHolon` and minted under the project's base (decision 0009). Each version holon is `cga:memberOf` its model holon. The model's current ref is recorded in the project's Weft configuration, as OQ3 requires, and the model holon holds the state of that ref.

| Holon layer | Content of the model holon |
|---|---|
| Interior | The current ref's normative graph, carried from that ref's version holon by a portal |
| Boundary | The current ref's boundary graphs, registered by IRI rather than copied |
| Projection | The thread projection, derived from the interior as it is for a version holon |
| Context | Model membership, the current ref, and the provenance of each refresh |

A refresh runs when the current ref changes or moves. It removes the previous ref's content from the interior before it traverses the portal from the new ref, because a rollback after the new traversal deletes the triples the two refs share. Weft passes an agent IRI minted under the project's base to every traversal, so each refresh has a provenance record. The current ref is read from the context layer and never from `derivation_chain`.

Nothing is authored in a model holon. A model that the versions do not derive (a reference architecture that a design refines, for example) is a model of its own in git, with its own model holon and version holons, and its relation to the refining model is carried by portals or alignment holons rather than by `cga:memberOf`.

## Consequences

Adapters, reports, and external links address the model holon, whose IRI does not change when the current ref does. A query about one ref, or a comparison of two, still addresses version holons through the scoped query helper ([zwelz3/holonic#52](https://github.com/zwelz3/holonic/issues/52)). The open question in that issue (whether the helper rejects a scope containing two versions of one thing) gains a structural test, since two members of one model holon are two versions of one model.

The model holon's interior is never a union of versions, so validating the model holon validates the current ref and OQ3 holds for it. Its cost is one materialized copy of the current ref's normative graph, rebuilt on each refresh.

A refresh needs two operations holonic does not provide: a traversal that replaces the target interior instead of adding to it, and the replacement of a registered boundary graph. Each needs a holonic issue, like the enhancements decision 0003 lists; neither is filed. Until they exist, a refresh is a SPARQL update against the backend, which bypasses holonic's metadata refresh.

Model holon IRIs and version holon IRIs join the graph contract ([docs/graph-contract.md](../graph-contract.md)), so a change to how they are minted is a data migration (AGENTS.md rule 3).

Decision 0003's layer table and OQ3 gain the model holon when this record is accepted.

## Open points

- What one model is: a repository, a project configuration, or a top-level package.
- Whether a model has one current ref, or a model holon per long-lived branch. `cga:memberOf` allows one parent, so a version holon cannot belong to both a per-branch aggregate and a per-model aggregate.
- Whether adapter portals target the model holon. Their triples would share its interior with the current ref's, and a content-matched rollback of one source can remove triples the other also supplied.

## Alternatives considered

A model holon whose interior holds every version. Rejected because it is the merged validation OQ3 rules out; in the probe the aggregate's membrane failed as soon as it held two versions.

A model holon with an empty interior, used only for membership and discovery. It needs no refresh and no holonic enhancement, and it leaves every consumer to resolve the current version holon itself. It is a subset of this decision, and it is enough if no consumer needs a fixed holon to query or to target with a portal.

A current-ref pointer in configuration with no model holon. Rejected because a portal names its source and target holons, so every portal that targets the model would be re-registered when the current ref changes.

Version-invariant content authored in the model holon. Rejected because the content would not be in any commit, which AGENTS.md rule 1 forbids.

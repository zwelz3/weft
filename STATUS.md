# Status

State of the project as of 2026-11-27. The session that changes the project's state updates this file before it ends; [AGENTS.md](AGENTS.md) holds the rules that do not change from session to session.

## Phase

Design, with a package skeleton and spike evidence. The repository holds decision records 0001 to 0009 and proposed record 0010, open questions OQ1 to OQ16, plans for the profile, the adopter's capabilities, and the 1.0 release, five thread queries, a draft graph contract, the results of spikes 1 and 2 under `spike/`, public stand-in data under `data/fprime-comccsds/`, and a `weft` package with no functionality beyond its version. CI builds the sysml-toolkit wheel at the pinned commit and runs the tests on Linux and Windows for Python 3.11 to 3.13.

## Blockers

Issues labeled `blocker` stop the next step of work; `blocked` marks work waiting on them or on something outside the project; `release-1.0` marks what has to be settled before 1.0.

| Issue | Blocks |
|---|---|
| [zwelz3/weft#15](https://github.com/zwelz3/weft/issues/15) Choose the domain for Weft's own vocabulary | The profile package and alignment file ([zwelz3/weft#21](https://github.com/zwelz3/weft/issues/21)), the projection namespace ([zwelz3/weft#18](https://github.com/zwelz3/weft/issues/18)), and 1.0 |
| [zwelz3/weft#17](https://github.com/zwelz3/weft/issues/17) Which requirement link types the adopter treats as distinct | The profile's trace metadata ([zwelz3/weft#21](https://github.com/zwelz3/weft/issues/21)) |
| [zwelz3/weft#16](https://github.com/zwelz3/weft/issues/16) The long-term architecture between Flexo and Kotar (OQ14) | Filing both upstream reports and any tier 1 work; not the profile, derivation, or reports |
| [zwelz3/weft#13](https://github.com/zwelz3/weft/issues/13) Kotar round trip (blocked on the Kotar container release) | Confirming that graphical editing in Kotar works at tier 0 (OQ11) |

## Settled

| Decision | Content |
|---|---|
| [0001](docs/decisions/0001-git-is-the-record.md) | SysML v2 textual notation in git is the record. Flexo MMS is an optional one-way mirror (tier 1), and every core feature works at tier 0 without a server. |
| [0002](docs/decisions/0002-sysml-toolkit-for-parsing-and-checking.md) | sysml-toolkit parses, checks, and converts to and from SysML v2 API JSON. |
| [0003](docs/decisions/0003-holonic-for-graph-organization.md) | holonic organizes the derived graphs, one holon per model version. |
| [0004](docs/decisions/0004-python.md) | Python, 3.11 or later. |
| [0005](docs/decisions/0005-component-stereotype.md) | Component is a role. A required, open `bearer` list records whether a material artifact bears it, the material entity carrying an information content entity's concretization does, or a project-declared kind does. Accepted 2026-10-08. |
| [0006](docs/decisions/0006-interface-stereotype.md) | Interface applies to definitions and usages. Without `individual` they are specifications (prescriptive information content entity). With `individual` they are realized connections (material entity) linked to the specification they specialize, with no subclass axiom across the two. Accepted 2026-10-08, revised 2026-11-26. |
| [0007](docs/decisions/0007-action-definition-stereotype.md) | The `action def` stereotype is named Process and aligns to BFO process, because CCO's Function is a disposition. Accepted 2026-10-08. |
| [0008](docs/decisions/0008-requirement-stereotype.md) | Requirement needs no metadata tag: the metaclass classifies, and the declared short name identifies a requirement the thread links to. Requirement statements align to CCO prescriptive information content entity, not to the requirement checks SysML defines as instances. Accepted 2026-11-26; a user story is a requirement or concern with a stakeholder. |
| [0009](docs/decisions/0009-iri-bases.md) | Standard-library elements keep OMG's identifiers; each project and library package mints under its own configured base. Accepted 2026-11-26. |

## Open work

| Item | Location | State | Next action |
|---|---|---|---|
| Model holon | [docs/decisions/0010-model-holon.md](docs/decisions/0010-model-holon.md) | Proposed: a `cga:AggregateHolon` per model holds the current ref, and version holons are its members | The person accepts, revises, or rejects it. On acceptance, decision 0003 and OQ3 gain the model holon, and two holonic issues are filed (replace-mode traversal, boundary replacement) |
| Adopter capabilities | [docs/plans/adopter-capabilities.md](docs/plans/adopter-capabilities.md) | Drafted; four of five questions answered | User stories are requirements or concerns with a stakeholder (decision 0008). Link types: [zwelz3/weft#17](https://github.com/zwelz3/weft/issues/17). Kotar check: [zwelz3/weft#13](https://github.com/zwelz3/weft/issues/13) |
| Data for the spike | [zwelz3/weft#1](https://github.com/zwelz3/weft/issues/1) | Public stand-in merged in [zwelz3/weft#10](https://github.com/zwelz3/weft/pull/10) under `data/fprime-comccsds/`; the issue stays open for the adopter's own component | Use the stand-in in [zwelz3/weft#22](https://github.com/zwelz3/weft/issues/22) |
| Spikes 1 and 2 | [spike/RESULTS.md](spike/RESULTS.md) | Done; merged in [zwelz3/weft#8](https://github.com/zwelz3/weft/pull/8) and [zwelz3/weft#9](https://github.com/zwelz3/weft/pull/9), and [zwelz3/weft#2](https://github.com/zwelz3/weft/issues/2) closed | Steps 6 and 7 on the F Prime data: [zwelz3/weft#22](https://github.com/zwelz3/weft/issues/22) |
| Release 1.0 gates | [docs/plans/release-1.0.md](docs/plans/release-1.0.md) | Listed | [zwelz3/weft#15](https://github.com/zwelz3/weft/issues/15) (vocabulary domain), [zwelz3/weft#18](https://github.com/zwelz3/weft/issues/18) (OQ15), [zwelz3/weft#19](https://github.com/zwelz3/weft/issues/19) (OQ16), and [zwelz3/weft#20](https://github.com/zwelz3/weft/issues/20) (ontologist review) |
| Stable identity on SysML v2 | [zwelz3/weft#12](https://github.com/zwelz3/weft/issues/12) | Tracked | Requirements keyed by short name, claims by their ends, a thin sidecar for other linked elements |
| Profile | [docs/plans/profile-brief.md](docs/plans/profile-brief.md) | Stereotypes decided in 0005 to 0008 | Write the profile package and alignment file: [zwelz3/weft#21](https://github.com/zwelz3/weft/issues/21), blocked by [zwelz3/weft#15](https://github.com/zwelz3/weft/issues/15) and, for trace metadata, [zwelz3/weft#17](https://github.com/zwelz3/weft/issues/17) |
| Report to sysml-toolkit maintainers | [docs/outreach/sysml-toolkit-rename-stable-identity.md](docs/outreach/sysml-toolkit-rename-stable-identity.md) | Drafted, to be filed | Blocked by [zwelz3/weft#16](https://github.com/zwelz3/weft/issues/16) (OQ14). Add the identity evidence from [zwelz3/weft#12](https://github.com/zwelz3/weft/issues/12) before filing |
| Report to Flexo maintainers | [docs/outreach/flexo-sysmlv2-rdf.md](docs/outreach/flexo-sysmlv2-rdf.md) | Drafted and reviewed, to be filed | Blocked by [zwelz3/weft#16](https://github.com/zwelz3/weft/issues/16) (OQ14) |
| holonic enhancements | [#51](https://github.com/zwelz3/holonic/issues/51), [#52](https://github.com/zwelz3/holonic/issues/52), [#53](https://github.com/zwelz3/holonic/issues/53) | #30 and #50 merged to holonic `main` in [zwelz3/holonic#54](https://github.com/zwelz3/holonic/pull/54), with two defects found during that work fixed in [zwelz3/holonic#56](https://github.com/zwelz3/holonic/pull/56); not yet released | Until holonic 0.9.0 is released, Weft pins holonic `main` at `067f5ea` (decision 0003), the merge of #56, which follows #54. #52 after spike step 7, which supplies its two-version fixture. #51 and #53 deferred: the adopter needs no cross-source identity yet, and Kotar works against git rather than Flexo |

The design questions behind this work are in [docs/OPEN-QUESTIONS.md](docs/OPEN-QUESTIONS.md) (OQ1 to OQ16).

## Versions reviewed

| Project | Version | How it was reviewed |
|---|---|---|
| [sysml-toolkit](https://github.com/Open-MBEE/sysml-toolkit) | 0.10.2, pinned at `821221767c3c56cb1ebe7da22666197a47c9c645` with SysML-v2-Release at `de1070ae8e79c21532b8004fc663d47b35d0e9fa` (decision 0002) | First from a source archive of `main` with no commit hash recorded, then from a clone at `821221767c3c56cb1ebe7da22666197a47c9c645`, built with Rust 1.97 and run against SysML-v2-Release `de1070ae8e79c21532b8004fc663d47b35d0e9fa` (fetched with `git submodule update --init spec-refs/SysML-v2-Release`). The probe's results are in [docs/plans/adopter-capabilities.md](docs/plans/adopter-capabilities.md). |
| [flexo-mms-sysmlv2](https://github.com/Open-MBEE/flexo-mms-sysmlv2) | Commit `61d1c9da77e1f0eebd4734290b8bb04fb04162f0` | Clone |
| [holonic](https://github.com/zwelz3/holonic) | `main`, reviewed at `d8d1758752827c35fc6781e89e01557b6e5e1825` after the 0.8.0 release; pinned at `067f5ea2bdeeb2f7415593def90188b213d029f3`, the merge of #56 (decision 0003) | Clone and source archive |
| [OpenSysML](https://github.com/Open-MBEE/OpenSysML) | Documentation only; `main` was at `a5bd7eb7d8462ff1308cfab7b1046f58245e3d53` on 2026-10-08 | README on pkg.go.dev, which is not tied to a commit; opensysml.org was unreachable from the session that reviewed it |

## Findings that are easy to rediscover

- The toolkit's Python package is named `sysmlv2`, and that name on PyPI belongs to an unrelated placeholder project. The bindings are built from source (decision 0002).
- Flexo's per-ref SPARQL endpoints choose the dataset only for queries that name no graphs, and holonic's layer reads use `GRAPH` patterns ([zwelz3/holonic#53](https://github.com/zwelz3/holonic/issues/53)).
- holonic validates the union of a holon's interior graphs, so two model versions cannot share a holon (OQ3).
- Claude Code reads `AGENTS.md` when no `CLAUDE.md` exists in the working directory or above it (v2.1.277 or later). Adding a `CLAUDE.md` to this repository stops that unless the new file imports `@AGENTS.md`.

## Working conventions

The maintainer pushes directly to `main` while the project is in design; contributions arrive as pull requests on this repository, stacked when one depends on another. Commits are authored by the maintainer, and agents add no AI attribution to commits or to pull request bodies (AGENTS.md rule 11). Documents are drafted with the `better-language-skill` skill.

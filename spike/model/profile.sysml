// Spike 2 revision: brought in line with the textual forms decisions 0005
// to 0007 state, in place of spike 1's stand-in enum-based `bearer` and
// definition-only `Interface`. Still disposable (AGENTS.md rule 8 applies
// to the real `weft` corpus, not to this package); the profile work proper
// is docs/plans/profile-brief.md.
library package StandInProfile {

	// Mirrors decision 0005's accepted textual form: an open attribute
	// def, not an enumeration, because sysml-toolkit 0.10.2 rejects an
	// enumeration that specializes another (`validateDefinitionVariationSpecialization`),
	// so an enumeration could not be extended outside the profile. `material`
	// and `information` are the profile's two declared values; a project
	// adds its own attribute usage of type `BearerKind` rather than a new
	// enum literal.
	attribute def BearerKind;
	attribute material : BearerKind;
	attribute information : BearerKind;

	// Mirrors decision 0005. Applies to `part def` and `part`. `[1..*]`:
	// the list of bearer values on one element is open and non-empty.
	metadata def Component {
		attribute bearer : BearerKind[1..*];
	}

	// Mirrors decision 0006. Applies to `interface def`, `port def`,
	// `interface`, and `port`. The `individual` keyword on the stereotyped
	// element selects specification (no `individual`) vs. realized
	// connection (`individual`); Weft adds no separate instance tag.
	metadata def Interface;

	// Mirrors decision 0007. Applies to `action def`.
	metadata def Process;
}

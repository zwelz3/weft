// Spike 1 step 5: the pump system's definitions, moved into a library
// package so step 5 (ontology export) exports reusable classes rather than
// a model's usages (OQ4: "Ontologies are exported from SysML library
// packages so that a domain definition is reused across models rather than
// minted again by each one"). pump-system.sysml imports this package and
// keeps only usages, requirements, and the satisfy/verify relationships.
library package PumpLibrary {
	private import ScalarValues::*;
	private import StandInProfile::*;

	#Interface port def PowerPort;
	#Interface interface def DataLink;

	#Process action def MonitorPressure {
		in pressureReading : Real;
		out alarm : Boolean;
	}

	// A project-declared bearer value (decision 0005: "a project adds a
	// value by declaring an attribute usage of type BearerKind in its own
	// package"), minted under this spike's own package rather than the
	// profile's.
	attribute thirdPartyBinary : BearerKind;

	part def PumpSystem {
		@Component { bearer = material; }

		part <'CMP-PUMP'> pump : Pump;
		part <'CMP-CTRL'> controller : Controller;
		part <'CMP-SENS'> sensor : PressureSensor;
		part <'CMP-ENCL'> enclosure : Enclosure;

		port powerIn : PowerPort;
		interface dataLink : DataLink;

		perform action monitor : MonitorPressure;
	}

	part def Pump {
		@Component { bearer = material; }
		port powerPort : PowerPort;
	}

	part def Controller {
		@Component { bearer = information; }
		interface dataPort : DataLink;
	}

	part def PressureSensor {
		@Component { bearer = material; }
	}

	part def Enclosure {
		@Component { bearer = material; }
	}

	// A two-valued bearer (decision 0005: "an element with more than one
	// value gets the alignment axioms of each value; firmware shipped on a
	// chip is one element with bearer = (material, information)").
	part def EmbeddedController {
		@Component { bearer = (material, information); }
	}

	// A component whose bearer is the project-declared value above, not
	// one of the profile's two.
	part def ThirdPartyModule {
		@Component { bearer = thirdPartyBinary; }
	}

	// An individual interface def and usage (decision 0006): the realized
	// connection between the controller and the sensor, specializing the
	// DataLink specification. `individual` selects the realized-connection
	// reading; the specialization (`:>`) is the object-property link the
	// derivation emits to the specification class (AGENTS.md rule 5).
	#Interface individual interface def ControllerSensorLink :> DataLink;

	requirement def MaxPressureDef {
		doc /* The system shall limit sustained pressure to 10 bar. */
		subject system : PumpSystem;
	}

	requirement def ResponseTimeDef {
		doc /* The controller shall raise an alarm within 200 ms of an over-pressure reading. */
		subject system : PumpSystem;
	}

	verification def PumpSystemAcceptance {
		objective acceptanceObjective {
			verify requirement maxPressureVerdict : MaxPressureDef;
			verify requirement responseTimeVerdict : ResponseTimeDef;
		}
	}
}

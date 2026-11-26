# Step 6 findings

`spike/shapes/instances.csv` is a stand-in instance table (28 rows: 10 with an injected fault, 18
clean), written for this spike because the real adopter's instance table has not arrived yet
([zwelz3/weft#1](https://github.com/zwelz3/weft/issues/1), STATUS.md "Data for the spike"). It
exercises the five component classes (`PumpSystem`, `Pump`, `Controller`, `PressureSensor`,
`Enclosure`) and four fault kinds: wrong value type, missing required value, cardinality, and
dangling reference. No row carries a wrong `rdf:type`, so the table does not test whether a record
of an untargeted class is reported (OQ6). Step 6 repeats against the real adopter table once it
arrives; this run establishes whether the derivation's shapes catch faults of these kinds at all
(M6).

## Reading the results

A fault counts as caught when the report has a result for the faulty row on the property the fault
concerns. The first version of `validate.py` counted a fault as caught when its row had any result.
That count is not informative on this table, because the shapes flag 10 of the 18 clean rows: every
`PumpSystem`, `Pump`, and `Controller` row. `shacl_export.py` derives `sh:minCount 1` for every
nested typed feature that declares no multiplicity, and four of those features are
ports or interfaces (`PumpSystem.powerIn`, `PumpSystem.dataLink`, `Pump.powerPort`,
`Controller.dataPort`) for which the table has no column. 20 of the validation results come from
those four shapes: 20 of 30 in spike 1's run and 20 of 28 in the run below. A table from the
adopter would need columns for these features, or the derivation would need multiplicities
declared in the model, before a clean row validates.

## Spike 2 step 2: a shape set that targets the toolkit's own class names

`spike/shapes/normative-shapes.ttl` states three profile shapes over the toolkit's own
metaclasses (`sysml:MetadataUsage`, `sysml:AttributeUsage`, and `sysml:InterfaceDefinition`, as
they appear in `spike/normative/output/pump-system.ttl`) rather than over the step 5 OWL export
classes. `spike/shapes/test_shacl_export.py` asserts that each shape has a focus node on the real
pump-system normative graph that satisfies the shape's SPARQL precondition, and that a deliberately
malformed node triggers a Violation. These three shapes are therefore not vacuous on the raw graph.

This does not close the membrane gap `spike/holons/BACKENDS.md` records (step 5/6's shapes, as the
normative holon's boundary, target none of the graph's nodes). `normative-shapes.ttl` is not
loaded as that boundary, and loaded as one it leaves 612 of the graph's 630 typed subjects
untargeted. holonic's `MembraneResult.untargeted`, with `cga:untargetedTypeSeverity sh:Violation`
declared in the boundary, is the detector for that gap (`spike/RESULTS.md`, spike 2 step 1).

The toolkit stores a metadata feature's assigned value (`@Component { bearer = material; }`) behind
a FeatureValue expression tree, not a direct triple from the MetadataUsage to the value: a single
value sits behind a `FeatureReferenceExpression`'s `tk:referent`, and a parenthesized multi-value
list (`bearer = (material, information)`) adds an `OperatorExpression` with `tk:argument` branches
above that. `ComponentBearerMinCountShape`'s property path, `(tk:member|tk:argument)*/tk:referent`,
walks either shape to the assigned `AttributeUsage`. A derivation that flattens this into a single
triple (as the real Weft derivation eventually must, for the same reason `docs/graph-contract.md`
flattens other toolkit-AST shapes) would not need this path; this spike validates the raw toolkit
graph directly, per the brief, so the shape carries the walk instead.

decision 0006's alignment property (an individual interface def's specialization of the
specification it realizes) is already an object property in the raw toolkit graph:
`Subclassification`'s `tk:general` is an IRI, not a literal (AGENTS.md rule 5 holds here with no
extra derivation work), so `IndividualInterfaceLinkedToSpecificationShape` only has to assert the
link resolves to another `InterfaceDefinition`.

### M6 against the regenerated shapes

The generated part of this file, below, is the run against the shapes spike 2 regenerated from the
extended model (`spike/RESULTS.md`, spike 2 step 2), where `bearer` is `BearerKind[1..*]`, so the
bearer property shape has `sh:minCount 1` and no `sh:maxCount`. Spike 1's run, against shapes
derived from spike 1's model (`enum def BearerKind`, a single-valued `bearer`), had 30 validation
results and caught each of the 10 injected faults with the shape on the faulty property. The
regenerated shapes give 28 results and catch 8 of the 10:

| Row | Fault | Caught by its own shape | Shape that reports the row |
|---|---|---|---|
| SENS-06 | duplicate_bearer | no | none |
| CTRL-06 | duplicate_bearer | no | `Controller_dataPort-shape` only |

The other eight rows are caught as in spike 1. Neither `duplicate_bearer` row is caught, which is
correct under decision 0005: two distinct bearer values on one element are allowed, so the table's
`duplicate_bearer` rows are no longer faults. CTRL-06 still has a result, because the table gives
no Controller row a `dataPort`, so `Controller_dataPort-shape` reports every Controller row
(CTRL-01 to CTRL-06). Counting a fault as caught when its row has any result, as `validate.py` did
before spike 1's review, gives 9 of 10 on these shapes. This run does not rewrite the stand-in
table.

<!-- Generated by validate.py below this line. -->

pySHACL conforms: False. Validation results: 28.

Injected faults: 10. Caught by the shape on the faulty property: 8. Rows with any result: 9.

Clean rows: 18. Clean rows with at least one result (false positives): 10, on the properties Controller_dataPort, PumpSystem_dataLink, PumpSystem_powerIn, Pump_powerPort.

| Row | Fault | Caught by its own shape | Other properties flagged on the row |
|---|---|---|---|
| SYS-03 | dangling_ref | yes | PumpSystem_dataLink, PumpSystem_powerIn |
| SYS-04 | missing_required | yes | PumpSystem_dataLink, PumpSystem_powerIn |
| PUMP-05 | missing_bearer | yes | Pump_powerPort |
| PUMP-06 | wrong_bearer_type | yes | Pump_powerPort |
| CTRL-05 | missing_bearer | yes | Controller_dataPort |
| CTRL-06 | duplicate_bearer | no | Controller_dataPort |
| SENS-05 | wrong_bearer_type | yes | none |
| SENS-06 | duplicate_bearer | no | none |
| ENCL-05 | missing_bearer | yes | none |
| ENCL-06 | wrong_bearer_type | yes | none |

| Clean row | Properties flagged |
|---|---|
| SYS-01 | PumpSystem_dataLink, PumpSystem_powerIn |
| SYS-02 | PumpSystem_dataLink, PumpSystem_powerIn |
| PUMP-01 | Pump_powerPort |
| PUMP-02 | Pump_powerPort |
| PUMP-03 | Pump_powerPort |
| PUMP-04 | Pump_powerPort |
| CTRL-01 | Controller_dataPort |
| CTRL-02 | Controller_dataPort |
| CTRL-03 | Controller_dataPort |
| CTRL-04 | Controller_dataPort |
| SENS-01 | none |
| SENS-02 | none |
| SENS-03 | none |
| SENS-04 | none |
| ENCL-01 | none |
| ENCL-02 | none |
| ENCL-03 | none |
| ENCL-04 | none |

## Full pySHACL report

```
Validation Report
Conforms: False
Results (28):
Constraint Violation in ClassConstraintComponent (http://www.w3.org/ns/shacl#ClassConstraintComponent):
	Severity: sh:Violation
	Source Shape: <https://weft.ghostsystems.ai/spike1/pump-library/property/Component_bearer-shape>
	Focus Node: <https://weft.ghostsystems.ai/spike1/pump-library/instance/ENCL-06>
	Value Node: Literal("composite")
	Result Path: <https://weft.ghostsystems.ai/spike1/pump-library/property/Component_bearer>
	Message: Value does not have class <https://weft.ghostsystems.ai/spike1/pump-library/class/BearerKind>
Constraint Violation in ClassConstraintComponent (http://www.w3.org/ns/shacl#ClassConstraintComponent):
	Severity: sh:Violation
	Source Shape: <https://weft.ghostsystems.ai/spike1/pump-library/property/Component_bearer-shape>
	Focus Node: <https://weft.ghostsystems.ai/spike1/pump-library/instance/PUMP-06>
	Value Node: Literal("steel")
	Result Path: <https://weft.ghostsystems.ai/spike1/pump-library/property/Component_bearer>
	Message: Value does not have class <https://weft.ghostsystems.ai/spike1/pump-library/class/BearerKind>
Constraint Violation in ClassConstraintComponent (http://www.w3.org/ns/shacl#ClassConstraintComponent):
	Severity: sh:Violation
	Source Shape: <https://weft.ghostsystems.ai/spike1/pump-library/property/Component_bearer-shape>
	Focus Node: <https://weft.ghostsystems.ai/spike1/pump-library/instance/SENS-05>
	Value Node: Literal("metal")
	Result Path: <https://weft.ghostsystems.ai/spike1/pump-library/property/Component_bearer>
	Message: Value does not have class <https://weft.ghostsystems.ai/spike1/pump-library/class/BearerKind>
Constraint Violation in ClassConstraintComponent (http://www.w3.org/ns/shacl#ClassConstraintComponent):
	Severity: sh:Violation
	Source Shape: <https://weft.ghostsystems.ai/spike1/pump-library/property/PumpSystem_pump-shape>
	Focus Node: <https://weft.ghostsystems.ai/spike1/pump-library/instance/SYS-03>
	Value Node: <https://weft.ghostsystems.ai/spike1/pump-library/instance/PUMP-99>
	Result Path: <https://weft.ghostsystems.ai/spike1/pump-library/property/PumpSystem_pump>
	Message: Value does not have class <https://weft.ghostsystems.ai/spike1/pump-library/class/Pump>
Constraint Violation in MinCountConstraintComponent (http://www.w3.org/ns/shacl#MinCountConstraintComponent):
	Severity: sh:Violation
	Source Shape: <https://weft.ghostsystems.ai/spike1/pump-library/property/Component_bearer-shape>
	Focus Node: <https://weft.ghostsystems.ai/spike1/pump-library/instance/CTRL-05>
	Result Path: <https://weft.ghostsystems.ai/spike1/pump-library/property/Component_bearer>
	Message: Less than 1 values on <https://weft.ghostsystems.ai/spike1/pump-library/instance/CTRL-05>-><https://weft.ghostsystems.ai/spike1/pump-library/property/Component_bearer>
Constraint Violation in MinCountConstraintComponent (http://www.w3.org/ns/shacl#MinCountConstraintComponent):
	Severity: sh:Violation
	Source Shape: <https://weft.ghostsystems.ai/spike1/pump-library/property/Component_bearer-shape>
	Focus Node: <https://weft.ghostsystems.ai/spike1/pump-library/instance/ENCL-05>
	Result Path: <https://weft.ghostsystems.ai/spike1/pump-library/property/Component_bearer>
	Message: Less than 1 values on <https://weft.ghostsystems.ai/spike1/pump-library/instance/ENCL-05>-><https://weft.ghostsystems.ai/spike1/pump-library/property/Component_bearer>
Constraint Violation in MinCountConstraintComponent (http://www.w3.org/ns/shacl#MinCountConstraintComponent):
	Severity: sh:Violation
	Source Shape: <https://weft.ghostsystems.ai/spike1/pump-library/property/Component_bearer-shape>
	Focus Node: <https://weft.ghostsystems.ai/spike1/pump-library/instance/PUMP-05>
	Result Path: <https://weft.ghostsystems.ai/spike1/pump-library/property/Component_bearer>
	Message: Less than 1 values on <https://weft.ghostsystems.ai/spike1/pump-library/instance/PUMP-05>-><https://weft.ghostsystems.ai/spike1/pump-library/property/Component_bearer>
Constraint Violation in MinCountConstraintComponent (http://www.w3.org/ns/shacl#MinCountConstraintComponent):
	Severity: sh:Violation
	Source Shape: <https://weft.ghostsystems.ai/spike1/pump-library/property/Controller_dataPort-shape>
	Focus Node: <https://weft.ghostsystems.ai/spike1/pump-library/instance/CTRL-01>
	Result Path: <https://weft.ghostsystems.ai/spike1/pump-library/property/Controller_dataPort>
	Message: Less than 1 values on <https://weft.ghostsystems.ai/spike1/pump-library/instance/CTRL-01>-><https://weft.ghostsystems.ai/spike1/pump-library/property/Controller_dataPort>
Constraint Violation in MinCountConstraintComponent (http://www.w3.org/ns/shacl#MinCountConstraintComponent):
	Severity: sh:Violation
	Source Shape: <https://weft.ghostsystems.ai/spike1/pump-library/property/Controller_dataPort-shape>
	Focus Node: <https://weft.ghostsystems.ai/spike1/pump-library/instance/CTRL-02>
	Result Path: <https://weft.ghostsystems.ai/spike1/pump-library/property/Controller_dataPort>
	Message: Less than 1 values on <https://weft.ghostsystems.ai/spike1/pump-library/instance/CTRL-02>-><https://weft.ghostsystems.ai/spike1/pump-library/property/Controller_dataPort>
Constraint Violation in MinCountConstraintComponent (http://www.w3.org/ns/shacl#MinCountConstraintComponent):
	Severity: sh:Violation
	Source Shape: <https://weft.ghostsystems.ai/spike1/pump-library/property/Controller_dataPort-shape>
	Focus Node: <https://weft.ghostsystems.ai/spike1/pump-library/instance/CTRL-03>
	Result Path: <https://weft.ghostsystems.ai/spike1/pump-library/property/Controller_dataPort>
	Message: Less than 1 values on <https://weft.ghostsystems.ai/spike1/pump-library/instance/CTRL-03>-><https://weft.ghostsystems.ai/spike1/pump-library/property/Controller_dataPort>
Constraint Violation in MinCountConstraintComponent (http://www.w3.org/ns/shacl#MinCountConstraintComponent):
	Severity: sh:Violation
	Source Shape: <https://weft.ghostsystems.ai/spike1/pump-library/property/Controller_dataPort-shape>
	Focus Node: <https://weft.ghostsystems.ai/spike1/pump-library/instance/CTRL-04>
	Result Path: <https://weft.ghostsystems.ai/spike1/pump-library/property/Controller_dataPort>
	Message: Less than 1 values on <https://weft.ghostsystems.ai/spike1/pump-library/instance/CTRL-04>-><https://weft.ghostsystems.ai/spike1/pump-library/property/Controller_dataPort>
Constraint Violation in MinCountConstraintComponent (http://www.w3.org/ns/shacl#MinCountConstraintComponent):
	Severity: sh:Violation
	Source Shape: <https://weft.ghostsystems.ai/spike1/pump-library/property/Controller_dataPort-shape>
	Focus Node: <https://weft.ghostsystems.ai/spike1/pump-library/instance/CTRL-05>
	Result Path: <https://weft.ghostsystems.ai/spike1/pump-library/property/Controller_dataPort>
	Message: Less than 1 values on <https://weft.ghostsystems.ai/spike1/pump-library/instance/CTRL-05>-><https://weft.ghostsystems.ai/spike1/pump-library/property/Controller_dataPort>
Constraint Violation in MinCountConstraintComponent (http://www.w3.org/ns/shacl#MinCountConstraintComponent):
	Severity: sh:Violation
	Source Shape: <https://weft.ghostsystems.ai/spike1/pump-library/property/Controller_dataPort-shape>
	Focus Node: <https://weft.ghostsystems.ai/spike1/pump-library/instance/CTRL-06>
	Result Path: <https://weft.ghostsystems.ai/spike1/pump-library/property/Controller_dataPort>
	Message: Less than 1 values on <https://weft.ghostsystems.ai/spike1/pump-library/instance/CTRL-06>-><https://weft.ghostsystems.ai/spike1/pump-library/property/Controller_dataPort>
Constraint Violation in MinCountConstraintComponent (http://www.w3.org/ns/shacl#MinCountConstraintComponent):
	Severity: sh:Violation
	Source Shape: <https://weft.ghostsystems.ai/spike1/pump-library/property/PumpSystem_dataLink-shape>
	Focus Node: <https://weft.ghostsystems.ai/spike1/pump-library/instance/SYS-01>
	Result Path: <https://weft.ghostsystems.ai/spike1/pump-library/property/PumpSystem_dataLink>
	Message: Less than 1 values on <https://weft.ghostsystems.ai/spike1/pump-library/instance/SYS-01>-><https://weft.ghostsystems.ai/spike1/pump-library/property/PumpSystem_dataLink>
Constraint Violation in MinCountConstraintComponent (http://www.w3.org/ns/shacl#MinCountConstraintComponent):
	Severity: sh:Violation
	Source Shape: <https://weft.ghostsystems.ai/spike1/pump-library/property/PumpSystem_dataLink-shape>
	Focus Node: <https://weft.ghostsystems.ai/spike1/pump-library/instance/SYS-02>
	Result Path: <https://weft.ghostsystems.ai/spike1/pump-library/property/PumpSystem_dataLink>
	Message: Less than 1 values on <https://weft.ghostsystems.ai/spike1/pump-library/instance/SYS-02>-><https://weft.ghostsystems.ai/spike1/pump-library/property/PumpSystem_dataLink>
Constraint Violation in MinCountConstraintComponent (http://www.w3.org/ns/shacl#MinCountConstraintComponent):
	Severity: sh:Violation
	Source Shape: <https://weft.ghostsystems.ai/spike1/pump-library/property/PumpSystem_dataLink-shape>
	Focus Node: <https://weft.ghostsystems.ai/spike1/pump-library/instance/SYS-03>
	Result Path: <https://weft.ghostsystems.ai/spike1/pump-library/property/PumpSystem_dataLink>
	Message: Less than 1 values on <https://weft.ghostsystems.ai/spike1/pump-library/instance/SYS-03>-><https://weft.ghostsystems.ai/spike1/pump-library/property/PumpSystem_dataLink>
Constraint Violation in MinCountConstraintComponent (http://www.w3.org/ns/shacl#MinCountConstraintComponent):
	Severity: sh:Violation
	Source Shape: <https://weft.ghostsystems.ai/spike1/pump-library/property/PumpSystem_dataLink-shape>
	Focus Node: <https://weft.ghostsystems.ai/spike1/pump-library/instance/SYS-04>
	Result Path: <https://weft.ghostsystems.ai/spike1/pump-library/property/PumpSystem_dataLink>
	Message: Less than 1 values on <https://weft.ghostsystems.ai/spike1/pump-library/instance/SYS-04>-><https://weft.ghostsystems.ai/spike1/pump-library/property/PumpSystem_dataLink>
Constraint Violation in MinCountConstraintComponent (http://www.w3.org/ns/shacl#MinCountConstraintComponent):
	Severity: sh:Violation
	Source Shape: <https://weft.ghostsystems.ai/spike1/pump-library/property/PumpSystem_enclosure-shape>
	Focus Node: <https://weft.ghostsystems.ai/spike1/pump-library/instance/SYS-04>
	Result Path: <https://weft.ghostsystems.ai/spike1/pump-library/property/PumpSystem_enclosure>
	Message: Less than 1 values on <https://weft.ghostsystems.ai/spike1/pump-library/instance/SYS-04>-><https://weft.ghostsystems.ai/spike1/pump-library/property/PumpSystem_enclosure>
Constraint Violation in MinCountConstraintComponent (http://www.w3.org/ns/shacl#MinCountConstraintComponent):
	Severity: sh:Violation
	Source Shape: <https://weft.ghostsystems.ai/spike1/pump-library/property/PumpSystem_powerIn-shape>
	Focus Node: <https://weft.ghostsystems.ai/spike1/pump-library/instance/SYS-01>
	Result Path: <https://weft.ghostsystems.ai/spike1/pump-library/property/PumpSystem_powerIn>
	Message: Less than 1 values on <https://weft.ghostsystems.ai/spike1/pump-library/instance/SYS-01>-><https://weft.ghostsystems.ai/spike1/pump-library/property/PumpSystem_powerIn>
Constraint Violation in MinCountConstraintComponent (http://www.w3.org/ns/shacl#MinCountConstraintComponent):
	Severity: sh:Violation
	Source Shape: <https://weft.ghostsystems.ai/spike1/pump-library/property/PumpSystem_powerIn-shape>
	Focus Node: <https://weft.ghostsystems.ai/spike1/pump-library/instance/SYS-02>
	Result Path: <https://weft.ghostsystems.ai/spike1/pump-library/property/PumpSystem_powerIn>
	Message: Less than 1 values on <https://weft.ghostsystems.ai/spike1/pump-library/instance/SYS-02>-><https://weft.ghostsystems.ai/spike1/pump-library/property/PumpSystem_powerIn>
Constraint Violation in MinCountConstraintComponent (http://www.w3.org/ns/shacl#MinCountConstraintComponent):
	Severity: sh:Violation
	Source Shape: <https://weft.ghostsystems.ai/spike1/pump-library/property/PumpSystem_powerIn-shape>
	Focus Node: <https://weft.ghostsystems.ai/spike1/pump-library/instance/SYS-03>
	Result Path: <https://weft.ghostsystems.ai/spike1/pump-library/property/PumpSystem_powerIn>
	Message: Less than 1 values on <https://weft.ghostsystems.ai/spike1/pump-library/instance/SYS-03>-><https://weft.ghostsystems.ai/spike1/pump-library/property/PumpSystem_powerIn>
Constraint Violation in MinCountConstraintComponent (http://www.w3.org/ns/shacl#MinCountConstraintComponent):
	Severity: sh:Violation
	Source Shape: <https://weft.ghostsystems.ai/spike1/pump-library/property/PumpSystem_powerIn-shape>
	Focus Node: <https://weft.ghostsystems.ai/spike1/pump-library/instance/SYS-04>
	Result Path: <https://weft.ghostsystems.ai/spike1/pump-library/property/PumpSystem_powerIn>
	Message: Less than 1 values on <https://weft.ghostsystems.ai/spike1/pump-library/instance/SYS-04>-><https://weft.ghostsystems.ai/spike1/pump-library/property/PumpSystem_powerIn>
Constraint Violation in MinCountConstraintComponent (http://www.w3.org/ns/shacl#MinCountConstraintComponent):
	Severity: sh:Violation
	Source Shape: <https://weft.ghostsystems.ai/spike1/pump-library/property/Pump_powerPort-shape>
	Focus Node: <https://weft.ghostsystems.ai/spike1/pump-library/instance/PUMP-01>
	Result Path: <https://weft.ghostsystems.ai/spike1/pump-library/property/Pump_powerPort>
	Message: Less than 1 values on <https://weft.ghostsystems.ai/spike1/pump-library/instance/PUMP-01>-><https://weft.ghostsystems.ai/spike1/pump-library/property/Pump_powerPort>
Constraint Violation in MinCountConstraintComponent (http://www.w3.org/ns/shacl#MinCountConstraintComponent):
	Severity: sh:Violation
	Source Shape: <https://weft.ghostsystems.ai/spike1/pump-library/property/Pump_powerPort-shape>
	Focus Node: <https://weft.ghostsystems.ai/spike1/pump-library/instance/PUMP-02>
	Result Path: <https://weft.ghostsystems.ai/spike1/pump-library/property/Pump_powerPort>
	Message: Less than 1 values on <https://weft.ghostsystems.ai/spike1/pump-library/instance/PUMP-02>-><https://weft.ghostsystems.ai/spike1/pump-library/property/Pump_powerPort>
Constraint Violation in MinCountConstraintComponent (http://www.w3.org/ns/shacl#MinCountConstraintComponent):
	Severity: sh:Violation
	Source Shape: <https://weft.ghostsystems.ai/spike1/pump-library/property/Pump_powerPort-shape>
	Focus Node: <https://weft.ghostsystems.ai/spike1/pump-library/instance/PUMP-03>
	Result Path: <https://weft.ghostsystems.ai/spike1/pump-library/property/Pump_powerPort>
	Message: Less than 1 values on <https://weft.ghostsystems.ai/spike1/pump-library/instance/PUMP-03>-><https://weft.ghostsystems.ai/spike1/pump-library/property/Pump_powerPort>
Constraint Violation in MinCountConstraintComponent (http://www.w3.org/ns/shacl#MinCountConstraintComponent):
	Severity: sh:Violation
	Source Shape: <https://weft.ghostsystems.ai/spike1/pump-library/property/Pump_powerPort-shape>
	Focus Node: <https://weft.ghostsystems.ai/spike1/pump-library/instance/PUMP-04>
	Result Path: <https://weft.ghostsystems.ai/spike1/pump-library/property/Pump_powerPort>
	Message: Less than 1 values on <https://weft.ghostsystems.ai/spike1/pump-library/instance/PUMP-04>-><https://weft.ghostsystems.ai/spike1/pump-library/property/Pump_powerPort>
Constraint Violation in MinCountConstraintComponent (http://www.w3.org/ns/shacl#MinCountConstraintComponent):
	Severity: sh:Violation
	Source Shape: <https://weft.ghostsystems.ai/spike1/pump-library/property/Pump_powerPort-shape>
	Focus Node: <https://weft.ghostsystems.ai/spike1/pump-library/instance/PUMP-05>
	Result Path: <https://weft.ghostsystems.ai/spike1/pump-library/property/Pump_powerPort>
	Message: Less than 1 values on <https://weft.ghostsystems.ai/spike1/pump-library/instance/PUMP-05>-><https://weft.ghostsystems.ai/spike1/pump-library/property/Pump_powerPort>
Constraint Violation in MinCountConstraintComponent (http://www.w3.org/ns/shacl#MinCountConstraintComponent):
	Severity: sh:Violation
	Source Shape: <https://weft.ghostsystems.ai/spike1/pump-library/property/Pump_powerPort-shape>
	Focus Node: <https://weft.ghostsystems.ai/spike1/pump-library/instance/PUMP-06>
	Result Path: <https://weft.ghostsystems.ai/spike1/pump-library/property/Pump_powerPort>
	Message: Less than 1 values on <https://weft.ghostsystems.ai/spike1/pump-library/instance/PUMP-06>-><https://weft.ghostsystems.ai/spike1/pump-library/property/Pump_powerPort>

```

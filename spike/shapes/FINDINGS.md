# Step 6 findings

`spike/shapes/instances.csv` is a stand-in instance table (28 rows, 10 injected faults), written
for this spike because the real adopter's instance table has not arrived yet ([zwelz3/weft#1](https://github.com/zwelz3/weft/issues/1),
STATUS.md "Data for the spike"). It exercises the same five component classes
(`PumpSystem`, `Pump`, `Controller`, `PressureSensor`, `Enclosure`) and the four fault kinds the
spike brief asks for (wrong type, missing required, cardinality, dangling reference). Step 6
repeats against the real adopter table once it arrives; this run only establishes whether the
derivation's shapes catch faults of these kinds at all (M6).

pySHACL conforms: False

Injected faults: 10. Caught: 10.

| Row | Fault | Caught |
|---|---|---|
| SYS-03 | dangling_ref | yes |
| SYS-04 | missing_required | yes |
| PUMP-05 | missing_bearer | yes |
| PUMP-06 | wrong_bearer_type | yes |
| CTRL-05 | missing_bearer | yes |
| CTRL-06 | duplicate_bearer | yes |
| SENS-05 | wrong_bearer_type | yes |
| SENS-06 | duplicate_bearer | yes |
| ENCL-05 | missing_bearer | yes |
| ENCL-06 | wrong_bearer_type | yes |

## Full pySHACL report

```
Validation Report
Conforms: False
Results (30):
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
Constraint Violation in MaxCountConstraintComponent (http://www.w3.org/ns/shacl#MaxCountConstraintComponent):
	Severity: sh:Violation
	Source Shape: <https://weft.ghostsystems.ai/spike1/pump-library/property/Component_bearer-shape>
	Focus Node: <https://weft.ghostsystems.ai/spike1/pump-library/instance/CTRL-06>
	Result Path: <https://weft.ghostsystems.ai/spike1/pump-library/property/Component_bearer>
	Message: More than 1 values on <https://weft.ghostsystems.ai/spike1/pump-library/instance/CTRL-06>-><https://weft.ghostsystems.ai/spike1/pump-library/property/Component_bearer>
Constraint Violation in MaxCountConstraintComponent (http://www.w3.org/ns/shacl#MaxCountConstraintComponent):
	Severity: sh:Violation
	Source Shape: <https://weft.ghostsystems.ai/spike1/pump-library/property/Component_bearer-shape>
	Focus Node: <https://weft.ghostsystems.ai/spike1/pump-library/instance/SENS-06>
	Result Path: <https://weft.ghostsystems.ai/spike1/pump-library/property/Component_bearer>
	Message: More than 1 values on <https://weft.ghostsystems.ai/spike1/pump-library/instance/SENS-06>-><https://weft.ghostsystems.ai/spike1/pump-library/property/Component_bearer>
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

## Spike 2 step 2: a shape set that targets the toolkit's own class names

The gap above is closed by `spike/shapes/normative-shapes.ttl`: `sh:targetClass` values are
`sysml:MetadataUsage`, `sysml:AttributeUsage`, and `sysml:InterfaceDefinition` (the toolkit's own
metaclasses, as they appear in `spike/normative/output/pump-system.ttl`), not the step 5 OWL export
classes. `spike/shapes/test_shacl_export.py` asserts each shape has at least one focus node on the
real pump-system normative graph and that a deliberately malformed node triggers a Violation,
closing the non-vacuity gap this file first recorded.

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

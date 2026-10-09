# Step 5 export coverage

18 definitions declared, 18 exported as `owl:Class`.

| Metaclass | Name | Exported as |
|---|---|---|
| MetadataDefinition | Component | owl:Class |
| MetadataDefinition | Interface | owl:Class |
| MetadataDefinition | Process | owl:Class |
| PortDefinition | PowerPort | owl:Class |
| ConjugatedPortDefinition | ~PowerPort | owl:Class |
| InterfaceDefinition | DataLink | owl:Class |
| ActionDefinition | MonitorPressure | owl:Class |
| PartDefinition | PumpSystem | owl:Class |
| PartDefinition | Pump | owl:Class |
| PartDefinition | Controller | owl:Class |
| PartDefinition | PressureSensor | owl:Class |
| PartDefinition | Enclosure | owl:Class |
| PartDefinition | EmbeddedController | owl:Class |
| PartDefinition | ThirdPartyModule | owl:Class |
| InterfaceDefinition | ControllerSensorLink | owl:Class |
| RequirementDefinition | MaxPressureDef | owl:Class |
| RequirementDefinition | ResponseTimeDef | owl:Class |
| VerificationCaseDefinition | PumpSystemAcceptance | owl:Class |
| FeatureMembership | PumpSystem.pump | owl:ObjectProperty |
| FeatureMembership | PumpSystem.controller | owl:ObjectProperty |
| FeatureMembership | PumpSystem.sensor | owl:ObjectProperty |
| FeatureMembership | PumpSystem.enclosure | owl:ObjectProperty |
| FeatureMembership | PumpSystem.powerIn | owl:ObjectProperty |
| FeatureMembership | PumpSystem.dataLink | owl:ObjectProperty |
| FeatureMembership | Pump.powerPort | owl:ObjectProperty |
| FeatureMembership | Controller.dataPort | owl:ObjectProperty |

## Not exported

| Metaclass | Identifier | Why |
|---|---|---|
| FeatureMembership | MonitorPressure.pressureReading | feature's type is not an exported class (scalar-valued or untyped) |
| FeatureMembership | MonitorPressure.alarm | feature's type is not an exported class (scalar-valued or untyped) |

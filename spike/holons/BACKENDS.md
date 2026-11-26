# Step 7: holons, rdflib and Fuseki

## rdflib backend

`spike/holons/load_holons.py` builds a `holonic.HolonicDataset` on the default in-memory
`RdflibBackend`, with one holon per graph kind (decision 0003: a model version is a holon of its
own; this spike has one version of one model, so "per graph kind" rather than "per version"):

- `normative-pump-system`: interior is `spike/normative/output/pump-system.ttl` (step 3), boundary
  is `spike/shapes/shapes.ttl` (step 6).
- `projection-pump-system`: interior is `spike/projection/output.ttl` (step 4), no boundary.

Both holons load and both membranes report `conforms = True`. The full report is
`spike/holons/rdflib-report.md`.

The step 7 run used holonic `d8d1758` (`spike/ENVIRONMENT.md`), which predates the untargeted-node
report from [zwelz3/holonic#54](https://github.com/zwelz3/holonic/pull/54) (holonic issues #30 and
#50) and the fixes in [zwelz3/holonic#56](https://github.com/zwelz3/holonic/pull/56). The committed
report is from a re-run on holonic `067f5ea`, the merge of #56: the normative holon reports
`conforms = True`, health `intact`, no violations or warnings, and 507 untargeted nodes at Info
severity; the projection holon, which has no boundary, reports no untargeted nodes.

### A finding, not a clean pass

The normative holon's `conforms = True` is not evidence that step 6's shapes validate the
normative graph: pySHACL's report for it is `"Validation Report\nConforms: True\n"` with zero
violations and zero warnings, which is what pySHACL also reports when no shape's `sh:targetClass`
matches any node in the data graph. That is what happens here. Step 6's shapes target the class
IRIs step 5's OWL export mints (`https://weft.ghostsystems.ai/spike1/pump-library/class/Pump`, and
so on), but the normative graph types its nodes with the toolkit's own schema IRIs
(`https://www.omg.org/spec/SysML/20250201/PartDefinition`, and so on; step 3's element mapping).
No node in the normative graph is an instance of a step-5 class, so the membrane check is vacuous,
not passing.

Loading the normative graph with boundary shapes that actually target it needs a derivation from
definitions to shapes stated over the toolkit's own class IRIs, which is a different mapping from
step 5/6's export (that one is meant to validate exported instance data against exported classes,
not the normative graph against the toolkit's raw metaclasses). This spike does not build that
second mapping; it is a gap recorded against OQ6, which already covers the related question of
shapes that target nothing in a holon's interior (holonic's `cga:untargetedTypeSeverity`).

On holonic `067f5ea` the vacuous pass is visible in the result: all 507 typed nodes of the
normative graph are listed as untargeted. They are reported at Info, holonic's default, which does
not lower membrane health, so `conforms` and health are unchanged from the `d8d1758` run. With
`cga:untargetedTypeSeverity sh:Violation` added to the boundary, the same load reports health
`compromised` and the 507 nodes at Violation, while `conforms` stays `True`, because `conforms`
reflects the SHACL report alone (checked once by hand; `load_holons.py` does not set the severity).

## Fuseki backend

Not run. A listener answers on port 3030, but a plain HTTP request to it gets "Client sent an HTTP
request to an HTTPS server", and an HTTPS request fails the TLS handshake (`curl` exit 35); neither
response is what `holonic.backends.FusekiBackend` expects from a Fuseki dataset endpoint (Fuseki
serves plain HTTP by default), and no dataset name or credential is known for whatever is behind
that port. The environment does not otherwise mention a provisioned Fuseki instance. Fuseki run
deferred: no Fuseki instance is confirmed reachable without a credential in this spike's
environment.

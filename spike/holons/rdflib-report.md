# Step 7 holon load, rdflib backend

holonic commit `067f5ea2bdeeb2f7415593def90188b213d029f3`. Inputs: `spike/normative/output/pump-system.ttl` (14928 triples, 630 typed subjects), `spike/projection/output.ttl` (52 triples, 19 typed subjects), boundary `spike/shapes/shapes.ttl`. Load and validate took 1.97 s (one run).

This report gives counts. The full `MembraneResult` for each holon, with one untargeted-node entry per typed interior node, is written by rerunning this script with `--full-result <path>` (see `spike/holons/BACKENDS.md`); it is not committed.

## Normative holon `https://weft.ghostsystems.ai/spike1/holon/normative-pump-system`

| | |
|---|---|
| conforms | True |
| health | intact |
| violations | 0 |
| warnings | 0 |
| infos | 0 |
| untargeted nodes | 630 (by severity: Info: 630) |

## Projection holon `https://weft.ghostsystems.ai/spike1/holon/projection-pump-system`

| | |
|---|---|
| conforms | True |
| health | intact |
| violations | 0 |
| warnings | 0 |
| infos | 0 |
| untargeted nodes | 0 (by severity: none) |

Projection report text: `No boundary shapes defined.`

## Holarchy summary

```
HolarchySummary(holon_count=2, portal_count=0, root_count=2, health_distribution={'intact': 0, 'weakened': 0, 'compromised': 0}, stale_count=2, recent_activities=[])
```

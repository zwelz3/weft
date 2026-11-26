# Step 7: holons, rdflib and Fuseki

## rdflib backend

`spike/holons/load_holons.py` builds a `holonic.HolonicDataset` on the default in-memory
`RdflibBackend`, with one holon per graph kind (decision 0003: a model version is a holon of its
own; this spike has one version of one model, so "per graph kind" rather than "per version"):

- `normative-pump-system`: interior is `spike/normative/output/pump-system.ttl` (step 3), boundary
  is `spike/shapes/shapes.ttl` (step 6).
- `projection-pump-system`: interior is `spike/projection/output.ttl` (step 4), no boundary.

Both holons load and both membranes report `conforms = True`. The report is
`spike/holons/rdflib-report.md`. Spike 1 generated it at holonic `d8d1758` against spike 1's
normative graph (507 typed subjects, 12,068 triples). Spike 2 regenerated it at holonic `067f5ea`
(the merge of zwelz3/holonic#56 on `main`) against the graph this branch commits (630 typed
subjects, 14,928 triples, because step 2 extends the pump model), so it now carries holonic's
`untargeted` count, which `d8d1758` did not report.

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
second mapping; it is a gap worth recording against OQ6, which already covers the related question
of shapes that target nothing in a holon's interior (holonic's `cga:untargetedTypeSeverity`).

## Fuseki backend (spike 2, step 1)

Spike 1 deferred this because the shared listener on port 3030 answers TLS, not plain HTTP, and
carries no known dataset name or credential (AGENTS.md rule 1 also rules that listener out: it is
not a disposable instance this spike owns). Spike 2 runs a disposable Fuseki instead, per the
brief: Fuseki started with an in-memory dataset and stopped at the end of this section. This is a
tier-1 addition (AGENTS.md rule 1): it needs a running server, unlike the rdflib backend, which
every core Weft feature must still work without.

The committed `spike/holons/fuseki-report.md` comes from this run:

- **Version:** Apache Jena Fuseki 6.2.0, the standalone server jar
  `jena-fuseki-server-6.2.0.jar` from Maven Central
  (`https://repo1.maven.org/maven2/org/apache/jena/jena-fuseki-server/6.2.0/`), SHA-1
  `d3490295a2b95677c1227d25bca8564d40f993a7`, matching the published `.sha1`.
- **Runtime:** OpenJDK 21 on the host, with no container, because this environment had no running
  Docker daemon and `dlcdn.apache.org` (the distribution archive's host) was not reachable.
- **Command:** `java -jar jena-fuseki-server-6.2.0.jar --port=57027 --mem /ds`. `--mem` is
  Fuseki's in-memory, non-persistent dataset; nothing is written to disk and the dataset is gone
  when the process stops.
- **Port:** `57027` (host-local; not 3030, so there is no ambiguity with the shared listener this
  spike does not use). `spike/holons/test_load_holons.py` looks for Fuseki on this port.
- **Teardown:** stop the Java process.

An earlier run on this branch used the full distribution archive
(`apache-jena-fuseki-6.2.0.tar.gz`, SHA-512
`ba65f5867d2d4741b2ed9e2af5a0d4fbb447909894ab2a0c6bc4dac8997f4fe339c87b13c48d45d054977769f0f8bf763ea346b1f7792d5cdc458041bd43a132`)
inside an `eclipse-temurin:21-jre` container. Its report listed 507 untargeted nodes, which is spike
1's normative graph, not the 630-subject graph this branch commits, so it was replaced.

`spike/holons/load_holons.py` takes `--backend rdflib|fuseki` (default `rdflib`, unchanged from
spike 1) plus `--fuseki-url` / `--fuseki-dataset`, and builds a
`holonic.backends.fuseki_backend.FusekiBackend` for the Fuseki case (which needs `aiohttp`
installed). Both committed reports were generated at holonic `067f5ea` with:

```
python3 spike/holons/load_holons.py spike/normative/output/pump-system.ttl \
    spike/projection/output.ttl spike/shapes/shapes.ttl spike/holons/rdflib-report.md
python3 spike/holons/load_holons.py spike/normative/output/pump-system.ttl \
    spike/projection/output.ttl spike/shapes/shapes.ttl spike/holons/fuseki-report.md \
    --backend fuseki --fuseki-url http://127.0.0.1:57027 --fuseki-dataset ds
```

Each report gives counts. Adding `--full-result <path>` writes each holon's full `MembraneResult`
repr, whose untargeted list has one entry per typed interior node (about 130,000 characters for
this graph); that output is not committed. The full results from the two backends were compared
with `cmp` and are byte-identical. The holonic commit decision 0003 pins, `25d1c84`, gives the same
untargeted counts and health on the same graph (checked separately with that commit installed).

### Every difference between the two backends

| Aspect | rdflib | Fuseki |
|---|---|---|
| Needs a running service | No (in-process, in-memory) | Yes (disposable, started and stopped by this section) |
| Normative holon `conforms` / health | `True` / intact | `True` / intact |
| Normative holon untargeted nodes | 630 of 630 typed subjects, at Info | 630 of 630 typed subjects, at Info |
| Projection holon `conforms` / health | `True` / intact (no boundary) | `True` / intact (no boundary) |
| Violations / warnings / infos | 0 / 0 / 0 | 0 / 0 / 0 |
| Full `MembraneResult` repr | byte-identical to Fuseki's | byte-identical to rdflib's |
| Wall time for the load-and-validate run | 1.42 to 1.95 s over four runs | 4.01 to 4.63 s over four runs, each on a freshly started server (includes HTTP round trips to the dataset) |
| Persistence | None (process memory) | None here (`--mem`), but Fuseki also supports a persistent TDB2 dataset that rdflib's in-memory graph has no counterpart for |
| AGENTS.md tier | 0 (works offline) | 1 (needs a server; this section's addition) |

The two reports differ only in the backend name and the wall time. The finding from spike 1
(`conforms = True` is vacuous for the normative holon, because step 5/6's shapes target OWL export
classes the normative graph's nodes are not instances of) holds identically on both backends; it
is a boundary problem, not a backend difference. holonic already reports it: every one of the 630
typed subjects is in `MembraneResult.untargeted`, at Info severity because the boundary declares no
`cga:untargetedTypeSeverity`. Declaring `<holon> cga:untargetedTypeSeverity sh:Violation` in the
boundary leaves `conforms = True` (no SHACL result fires) and lowers health to compromised, which
is the detector a Weft membrane check needs; `spike/holons/test_load_holons.py` asserts both cases
on the real graph. Spike 2 step 2's `spike/shapes/normative-shapes.ttl` is not a boundary for this
holon: loaded as one, it leaves 612 of the 630 typed subjects untargeted (RESULTS.md, step 2).

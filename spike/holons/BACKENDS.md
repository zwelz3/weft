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
brief: a fresh download of Fuseki, started with an in-memory dataset, stopped at the end of this
section. This is a tier-1 addition (AGENTS.md rule 1): it needs a running server, unlike the
rdflib backend, which every core Weft feature must still work without.

- **Version:** Apache Jena Fuseki 6.2.0 (`apache-jena-fuseki-6.2.0.tar.gz` from
  `https://dlcdn.apache.org/jena/binaries/`, SHA-512
  `ba65f5867d2d4741b2ed9e2af5a0d4fbb447909894ab2a0c6bc4dac8997f4fe339c87b13c48d45d054977769f0f8bf763ea346b1f7792d5cdc458041bd43a132`,
  matching the published `.sha512`).
- **Runtime:** the `eclipse-temurin:21-jre` container image (already present in this environment),
  with the extracted Fuseki tree copied in via `docker cp` and run as the container's main process
  (bind-mounting the extracted tree did not work in this sandbox: the mounted directory appeared
  empty to the container even though `docker run -v parent:/data` for the parent directory listed
  it; `docker cp` into a long-lived container sidesteps that).
- **Command:** `java -jar fuseki-server.jar --port=57027 --mem /ds`, run with `docker exec -d` inside
  a container started with `docker run -d --network host eclipse-temurin:21-jre sleep 3600`.
  `--mem` is Fuseki's in-memory, non-persistent dataset; nothing is written to disk and the dataset
  is gone when the container stops.
- **Port:** `57027` (host-local, chosen free at the time; not 3030, so there is no ambiguity with
  the shared listener this spike does not use).
- **Teardown:** `docker stop <container-id>`; `--rm` on the `docker run` removes the container on
  stop, so no cleanup step is left behind.

`spike/holons/load_holons.py` now takes `--backend rdflib|fuseki` (default `rdflib`, unchanged from
spike 1) plus `--fuseki-url` / `--fuseki-dataset`, and builds a `holonic.backends.fuseki_backend.FusekiBackend`
for the Fuseki case. Both runs in this section use the same holonic commit (`25d1c84`, decision
0003's package pin — spike 1's rdflib report was generated against `d8d1758` per
`spike/ENVIRONMENT.md`, so it is not compared byte-for-byte here; this section regenerates an
rdflib run from the same commit as the Fuseki run for a fair diff).

### Every difference between the two backends

| Aspect | rdflib | Fuseki |
|---|---|---|
| Needs a running service | No (in-process, in-memory) | Yes (disposable, started and stopped by this section) |
| Normative holon `conforms` | `True` | `True` |
| Projection holon `conforms` | `True` | `True` |
| Violations / warnings / untargeted-node counts | identical | identical |
| `MembraneResult.report_text` | byte-identical to Fuseki's | byte-identical to rdflib's |
| Wall time for this section's load-and-validate run | 0.66 s | 1.16 s (HTTP round trips to the dataset) |
| Persistence | None (process memory) | None here (`--mem`), but Fuseki also supports a persistent TDB2 dataset that rdflib's in-memory graph has no counterpart for |
| AGENTS.md tier | 0 (works offline) | 1 (needs a server; this section's addition) |

Byte-for-byte, `spike/holons/fuseki-report.md` and an rdflib run taken at the same holonic commit
differ only in which backend name the report states. The finding from spike 1 (`conforms = True`
is vacuous for the normative holon, because step 5/6's shapes target OWL export classes the
normative graph's nodes are not instances of) holds identically on both backends; it is a shape
problem, not a backend difference, and is the gap addressed below in §2.

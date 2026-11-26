# Spike 1 environment

Disposable code and records for spike 1. Nothing under `spike/` is part of the `weft` package.

## Toolkit

sysml-toolkit 0.10.2, commit `821221767c3c56cb1ebe7da22666197a47c9c645`. Fetched the prebuilt binary
`sysmlv2-0.10.2-x86_64-unknown-linux-gnu.tar.gz` and `SHA256SUMS` from the GitHub release page into
`/tmp/spike1-toolkit/`. The archive's SHA-256 matched the published sum
(`cfa5a8e37cc1b427c82cdc51515fc5821bdcdd70e5f4d2095a7460f3520ba4c1`). Rust was not needed: the
release ships a working `sysmlv2` CLI binary with `convert --to full-json` for element ids with
derived properties and implied relationships, `check --strict`, `lint`, `verify`, and `describe`.
The binary is an ELF 64-bit executable; no build step ran.

A source clone of the toolkit at the same commit lives at `/tmp/spike1-toolkit-src/`, used only to
read `IDS.md` for the id-derivation scheme. The toolkit vendors SysML-v2-Release as the submodule
`spec-refs/SysML-v2-Release`, cloned separately for this spike (its remote is
`https://github.com/Systems-Modeling/SysML-v2-Release`, not `Open-MBEE/SysML-v2-Release`, which
does not exist) into `/tmp/spike1-sysml-release/`, checked out at `de1070ae8e79c21532b8004fc663d47b35d0e9fa`
per decision 0002.

## Id schemes offered

Per `IDS.md`, the toolkit derives every non-root user element's id as `uuid5(parent id, segment)`,
chained from the document root. Two graph formats exist in the Rust API: `GraphFormat::LegacyV2`
(scheme 2, the default) and `GraphFormat::CanonicalV3` (scheme 3, opt-in, exposed only through
`Model::with_graph_format` / `Session::from_sources_with_graph_format`). The 0.10.2 CLI's `convert`
command takes no flag to select a graph format, so the CLI always emits scheme 2. Measurement M1
and M2 (step 8) therefore report one scheme, not several; this narrows OQ2's framing of "per scheme
the CLI offers" to the single scheme the CLI exposes.

## Public model

`sysml/src/examples/Vehicle Example/SysML v2 Spec Annex A SimpleVehicleModel.sysml` and its sibling
units (`VehicleDefinitions.sysml`, `VehicleUsages.sysml`, `VehicleIndividuals.sysml`) in the release
clone, used as the public model required by step 2.

## Python environment

venv at `/tmp/spike1-venv/`, Python 3.12.3.

| Package | Version |
|---|---|
| rdflib | 7.6.0 |
| pyshacl | 0.40.1 |
| pytest | 9.1.1 |
| holonic | 0.9.0.dev0, installed from `git+https://github.com/zwelz3/holonic@d8d1758` per this brief |

holonic's commit here (`d8d1758752827c35fc6781e89e01557b6e5e1825`) is the one this brief specifies
and matches the "first reviewed" commit in decision 0003, not the `25d1c84` commit that decision
pins for the Weft package proper. Step 7 notes where this matters.

## Spike 2 step 1: holonic for the holon reports

The committed `spike/holons/rdflib-report.md` and `spike/holons/fuseki-report.md` were generated
with holonic installed from `git+https://github.com/zwelz3/holonic@067f5ea`
(`067f5ea2bdeeb2f7415593def90188b213d029f3`, the merge of zwelz3/holonic#56 on `main`), rdflib
7.6.0, pyshacl 0.40.2, and aiohttp 3.14.5 (which holonic's `FusekiBackend` imports), on Python
3.12.3. Decision 0003's pin, `25d1c84`, gives the same untargeted counts and health on the same
graph. `spike/holons/BACKENDS.md` records the Fuseki runtime.

## Spike 2 step 4: the Python bindings

The toolkit's `sysmlv2-py` crate, built with maturin at the same pinned commit
(`821221767c3c56cb1ebe7da22666197a47c9c645`), from a clone of the toolkit repository at that
commit:

```
cd crates/sysmlv2-py && maturin build --release -o <wheel-dir>
pip install <wheel-dir>/sysmlv2-0.10.2-cp39-abi3-manylinux_2_39_x86_64.whl
```

Rust toolchain: `rustc 1.99.0 (b940084d7 2026-09-28)`, installed with rustup (`--profile minimal`,
no shell-profile modification, since this environment's home directory is read-only); `maturin
1.15.0`. The build needed no changes to the toolkit source and produced one wheel, `sysmlv2-py`'s
`cdylib`, against CPython 3.12's `abi3-py3.9` ABI.

### id scheme 3 is not reachable through the bindings

M1 and M2 for id scheme 3 (`IDS.md`'s `GraphFormat::CanonicalV3`) do not run. The bindings build
cleanly (the brief's "if the bindings cannot be built" case does not apply), but
`crates/sysmlv2-py/src/lib.rs` wraps no graph-format selector. It exposes four `Session`
constructors: `from_files` and `from_sources` (both reach `TSession::from_sources_with_library`,
which passes `GraphFormat::LegacyV2`), `from_interchange_json` (`TSession::from_interchange_json_with_library`,
which lifts the JSON to text and builds with `GraphFormat::LegacyV2`), and `from_compact_cbor`
(`TSession::from_compact_cbor_with_library`, which takes the graph format named in the CBOR
payload's header). `from_compact_cbor` can therefore open a payload some other client encoded under
scheme 3, but no binding produces a scheme-3 model from textual notation.
`Session::from_sources_with_graph_format` is in `sysmlv2-transform` and `Model::with_graph_format`
in `sysmlv2-model`, below the Python binding; `IDS.md` already says the opt-in is "currently
exposed through the Rust APIs", and this spike confirms that the Python binding adds no exposure of
its own. `spike/ids/probe_scheme3.py` searches the binding crate's source for `graph_format`,
`GraphFormat`, and `canonical` and finds none. `spike/ids/test_probe_scheme3.py` repeats that
search against the toolkit checkout named by the `WEFT_TOOLKIT_SRC` environment variable (it skips
when the variable is unset), and checks the installed wheel's constructor names. Run against a
checkout of a later release, it fails if that release's binding crate mentions a graph-format API,
which is the cue to run M1 and M2 for scheme 3. This narrows OQ2 further than spike 1 did: at this
release, neither the CLI nor the Python bindings can build a scheme-3 model from textual notation.

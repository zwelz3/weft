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
`crates/sysmlv2-py/src/*.rs` wraps no graph-format selector: `Session.from_sources()` is the only
constructor exposed to Python, calling `TSession::from_sources`, which `IDS.md` states retains
`GraphFormat::LegacyV2` (scheme 2). `Session::from_sources_with_graph_format` and
`Model::with_graph_format` exist in `sysmlv2-model`, one layer below the Python binding, and
`IDS.md` already says as much for the Rust API generally ("the opt-in is currently exposed through
the Rust APIs") -- this spike confirms that the Python binding does not add its own exposure on
top. `spike/ids/probe_scheme3.py` greps the binding crate's source for every graph-format-related
identifier and finds none; `spike/ids/test_probe_scheme3.py` is the regression fence (it starts
failing the day a release adds the wrapper, which is the cue to run M1/M2 for scheme 3 for real).
This narrows OQ2 further than spike 1 did: not only does the CLI expose one scheme, so do the
Python bindings, at this release.

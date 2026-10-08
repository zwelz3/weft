"""Regression fence for spike 2 step 4: the bindings built at the pinned
commit (821221767c3c56cb1ebe7da22666197a47c9c645, spike/ENVIRONMENT.md) must
still expose no Python-reachable id-scheme selector, which is exactly why
M1/M2 could not be run for scheme 3 (IDS.md, "Opt-in canonical graphs"). If
a future toolkit release adds a `#[pymethods]`-wrapped graph-format
selector, this test starts failing and the M1/M2 scheme 3 numbers can be
run for real instead of being recorded as a capability gap.

Run directly: cd spike/ids && python3 -m pytest test_probe_scheme3.py
"""
import re
from pathlib import Path

PY_CRATE_SRC = Path("/tmp/weft-toolkit-2216793/st/crates/sysmlv2-py/src")


def test_sysmlv2_py_has_no_graph_format_selector():
    import pytest

    sysmlv2 = pytest.importorskip("sysmlv2", reason="bindings wheel not installed in this environment")

    assert not hasattr(sysmlv2.Session, "from_sources_with_graph_format")
    assert not hasattr(sysmlv2.Session, "from_interchange_json_with_graph_format")


def test_sysmlv2_py_source_mentions_no_graph_format_api():
    if not PY_CRATE_SRC.is_dir():
        import pytest

        pytest.skip("toolkit source checkout not present in this environment")
    pattern = re.compile(r"graph_format|GraphFormat|[Cc]anonical")
    hits = [f.name for f in PY_CRATE_SRC.glob("*.rs") if pattern.search(f.read_text())]
    assert hits == []

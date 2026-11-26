"""Regression fence for spike 2 step 4: at the pinned toolkit commit
(821221767c3c56cb1ebe7da22666197a47c9c645, spike/ENVIRONMENT.md) the
Python bindings expose no id-scheme selector, which is why M1/M2 could not
be run for scheme 3 (IDS.md, "Opt-in canonical graphs").

The source test reads the sysml-toolkit checkout named by the
WEFT_TOOLKIT_SRC environment variable (the repository root, containing
crates/sysmlv2-py) and skips when it is unset. It checks whichever commit
that checkout is at, so it describes the pinned release only when the
checkout is at the pinned commit; pointing it at a newer checkout is how to
recheck a later release. The module test checks the installed `sysmlv2`
wheel and skips when none is installed.

Run directly: cd spike/ids && WEFT_TOOLKIT_SRC=<toolkit checkout> python3 -m pytest test_probe_scheme3.py
"""
import os
import re
from pathlib import Path

import pytest

# The four Session constructors the bindings expose at the pinned commit.
# from_files and from_sources build from text with GraphFormat::LegacyV2,
# from_interchange_json lifts JSON to text and builds with LegacyV2, and
# from_compact_cbor takes the graph format named in the payload header, so
# it can open a payload another client encoded under scheme 3 but cannot
# produce one from textual notation.
SESSION_CONSTRUCTORS = {"from_files", "from_sources", "from_interchange_json", "from_compact_cbor"}


def _py_crate_src():
    root = os.environ.get("WEFT_TOOLKIT_SRC")
    if not root:
        pytest.skip("WEFT_TOOLKIT_SRC is unset; set it to a sysml-toolkit checkout to run this test")
    src = Path(root) / "crates" / "sysmlv2-py" / "src"
    if not src.is_dir():
        pytest.skip(f"WEFT_TOOLKIT_SRC={root} has no crates/sysmlv2-py/src")
    return src


def test_sysmlv2_py_has_no_graph_format_selector():
    sysmlv2 = pytest.importorskip("sysmlv2", reason="bindings wheel not installed in this environment")

    constructors = {n for n in dir(sysmlv2.Session) if n.startswith("from_")}
    assert constructors == SESSION_CONSTRUCTORS
    assert not hasattr(sysmlv2.Session, "from_sources_with_graph_format")
    assert not hasattr(sysmlv2.Session, "from_interchange_json_with_graph_format")


def test_sysmlv2_py_source_mentions_no_graph_format_api():
    src = _py_crate_src()
    pattern = re.compile(r"graph_format|GraphFormat|[Cc]anonical")
    hits = [f.name for f in src.glob("*.rs") if pattern.search(f.read_text(encoding="utf-8"))]
    assert hits == []

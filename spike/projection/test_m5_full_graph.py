"""Regression fence for spike 2 step 3: the five full-graph queries under
full-graph-queries/ must return the same result rows as the projected
queries under queries/, run against the same underlying model. A future
edit to either query set that silently changes what it selects (a dropped
FILTER, a wrong property) is caught here instead of only showing up as a
quiet drift between spike/RESULTS.md's projected and full-graph numbers.

Run directly: cd spike/projection && python3 -m pytest test_m5_full_graph.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import measure

REPO = Path(__file__).parent.parent.parent


def test_full_graph_queries_match_projected_queries_row_for_row(tmp_path):
    rows = measure.m5(tmp_path)
    assert len(rows) == 5
    for row in rows:
        assert row["results_equal"] is True, f"{row['query']}: full-graph and projected results differ"


def test_every_full_graph_query_file_has_a_projected_counterpart():
    full_dir = REPO / "spike/projection/full-graph-queries"
    proj_dir = REPO / "queries"
    full_names = {p.name for p in full_dir.glob("*.rq")}
    proj_names = {p.name for p in proj_dir.glob("*.rq")}
    assert full_names == proj_names
    assert len(full_names) == 5

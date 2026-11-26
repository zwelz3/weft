"""Regression fence for step 7: a boundary shape whose sh:targetClass
matches nothing in the interior must not be reported as a validating pass
in the same breath as a shape that actually fired. This guards the finding
BACKENDS.md records (the normative holon's True conforms is vacuous).
Run directly: cd spike/holons && python3 -m pytest test_load_holons.py
"""
import socket
from pathlib import Path

import pytest
from rdflib import RDF, Graph

import holonic
from holonic.model import MembraneHealth

NS = "https://weft.ghostsystems.ai/spike1/holons-test/"
FUSEKI_HOST, FUSEKI_PORT = "127.0.0.1", 57027


def _fuseki_reachable():
    try:
        with socket.create_connection((FUSEKI_HOST, FUSEKI_PORT), timeout=1):
            return True
    except OSError:
        return False


requires_fuseki = pytest.mark.skipif(
    not _fuseki_reachable(),
    reason=(
        "no disposable Fuseki reachable at "
        f"{FUSEKI_HOST}:{FUSEKI_PORT} (see BACKENDS.md for how spike 2 starts one); "
        "the rdflib tests above still run offline (AGENTS.md rule 1, rule 9)"
    ),
)


def test_vacuous_boundary_conforms_but_fires_no_shape():
    ds = holonic.HolonicDataset()
    holon = NS + "holon/empty-target"
    ds.add_holon(holon, "test holon")
    ds.add_interior(holon, f"<{NS}instance/thing> a <{NS}class/Unrelated> .")
    ds.add_boundary(
        holon,
        f"""
        @prefix sh: <http://www.w3.org/ns/shacl#> .
        <{NS}shape/Thing> a sh:NodeShape ;
            sh:targetClass <{NS}class/Thing> ;
            sh:property [ sh:path <{NS}property/required> ; sh:minCount 1 ] .
        """,
    )
    result = ds.validate_membrane(holon)
    assert result.conforms is True
    assert result.violations == []
    # Conforms is true only because no node in the interior is typed
    # NS:class/Thing; it is not evidence the required-property shape ran.


def test_declared_untargeted_severity_flags_the_vacuous_boundary():
    """holonic's untargeted report is the detector for the case above: with
    cga:untargetedTypeSeverity sh:Violation declared on the holon in its
    boundary, the same vacuous boundary still conforms (no SHACL result
    fires) but the membrane's health is COMPROMISED."""
    ds = holonic.HolonicDataset()
    holon = NS + "holon/declared-severity"
    ds.add_holon(holon, "test holon")
    ds.add_interior(holon, f"<{NS}instance/thing> a <{NS}class/Unrelated> .")
    ds.add_boundary(
        holon,
        f"""
        @prefix sh: <http://www.w3.org/ns/shacl#> .
        <{holon}> <urn:holonic:ontology:untargetedTypeSeverity> sh:Violation .
        <{NS}shape/Thing> a sh:NodeShape ;
            sh:targetClass <{NS}class/Thing> ;
            sh:property [ sh:path <{NS}property/required> ; sh:minCount 1 ] .
        """,
    )
    result = ds.validate_membrane(holon)
    assert result.conforms is True
    assert result.health is MembraneHealth.COMPROMISED
    assert [u.focus_node for u in result.untargeted] == [f"{NS}instance/thing"]


SPIKE = Path(__file__).parent.parent
NORMATIVE_GRAPH = SPIKE / "normative" / "output" / "pump-system.ttl"
REAL_HOLON = "https://weft.ghostsystems.ai/spike1/holon/normative-pump-system"
SEVERITY_VIOLATION = (
    f"<{REAL_HOLON}> <urn:holonic:ontology:untargetedTypeSeverity> "
    "<http://www.w3.org/ns/shacl#Violation> .\n"
)


def _validate_real_graph(boundary_text):
    ds = holonic.HolonicDataset()
    ds.add_holon(REAL_HOLON, "Pump system, normative graph", holon_type="cga:DataHolon")
    ds.add_interior(REAL_HOLON, NORMATIVE_GRAPH.read_text(encoding="utf-8"))
    ds.add_boundary(REAL_HOLON, boundary_text)
    return ds.validate_membrane(REAL_HOLON)


@pytest.mark.parametrize(
    "boundary, declare_violation, untargeted, health",
    [
        ("shapes/shapes.ttl", False, 630, MembraneHealth.INTACT),
        ("shapes/normative-shapes.ttl", False, 612, MembraneHealth.INTACT),
        ("shapes/shapes.ttl", True, 630, MembraneHealth.COMPROMISED),
    ],
)
def test_real_normative_graph_untargeted_counts(boundary, declare_violation, untargeted, health):
    """The numbers spike/RESULTS.md and BACKENDS.md cite: the pump-system
    normative graph has 630 typed subjects; step 6's shapes target none of
    them, step 2's normative shapes target 18, and every boundary conforms.
    Declaring sh:Violation as the untargeted severity is what changes the
    verdict, through health rather than conforms."""
    data = Graph().parse(NORMATIVE_GRAPH, format="turtle")
    assert len(set(data.subjects(RDF.type, None))) == 630
    text = (SPIKE / boundary).read_text(encoding="utf-8")
    result = _validate_real_graph((SEVERITY_VIOLATION if declare_violation else "") + text)
    assert result.conforms is True
    assert result.violations == []
    assert len(result.untargeted) == untargeted
    assert result.health is health


def test_matching_boundary_actually_catches_a_missing_required_property():
    ds = holonic.HolonicDataset()
    holon = NS + "holon/matching-target"
    ds.add_holon(holon, "test holon")
    ds.add_interior(holon, f"<{NS}instance/thing> a <{NS}class/Thing> .")
    ds.add_boundary(
        holon,
        f"""
        @prefix sh: <http://www.w3.org/ns/shacl#> .
        <{NS}shape/Thing> a sh:NodeShape ;
            sh:targetClass <{NS}class/Thing> ;
            sh:property [ sh:path <{NS}property/required> ; sh:minCount 1 ; sh:severity sh:Violation ] .
        """,
    )
    result = ds.validate_membrane(holon)
    assert result.conforms is False
    assert len(result.violations) >= 1


@requires_fuseki
def test_fuseki_backend_matches_rdflib_on_the_same_vacuous_boundary_case():
    """Regression fence for spike 2 step 1: the Fuseki backend must reach the
    same (vacuous) conforms verdict as rdflib on the exact case above, so a
    future change to FusekiBackend that silently drops the boundary graph (and
    so always conforms) is caught the same way the rdflib test catches it.
    """
    from holonic.backends.fuseki_backend import FusekiBackend

    backend = FusekiBackend(f"http://{FUSEKI_HOST}:{FUSEKI_PORT}", dataset="ds")
    ds = holonic.HolonicDataset(backend)
    holon = NS + "holon/fuseki-empty-target"
    ds.add_holon(holon, "test holon")
    ds.add_interior(holon, f"<{NS}instance/thing> a <{NS}class/Unrelated> .")
    ds.add_boundary(
        holon,
        f"""
        @prefix sh: <http://www.w3.org/ns/shacl#> .
        <{NS}shape/Thing> a sh:NodeShape ;
            sh:targetClass <{NS}class/Thing> ;
            sh:property [ sh:path <{NS}property/required> ; sh:minCount 1 ] .
        """,
    )
    result = ds.validate_membrane(holon)
    assert result.conforms is True
    assert result.violations == []

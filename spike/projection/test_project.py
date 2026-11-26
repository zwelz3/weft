"""Regression fence for step 4: the verify-report parser must match a real
`sysmlv2 verify` line, and the requirement/component CONSTRUCT queries must
only pick up elements that carry a declared short name (the definition-level
placeholder objectives in the model have none and must not leak into the
projection). Run directly:

    cd spike/projection && python3 -m pytest test_project.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from rdflib import Graph, Literal, Namespace, RDF, URIRef

import project

TK = Namespace("https://weft.ghostsystems.ai/spike1/toolkit-vocab#")
SYSML = Namespace("https://www.omg.org/spec/SysML/20250201/")


def test_verify_line_regex_matches_a_real_report_line():
    line = (
        "spike/model/pump-system.sysml:101:2  <anonymous> "
        "(SatisfyRequirementUsage, satisfies PumpSystemModel::MaxPressure "
        "by pumpSystemUnderTest): undecided (the requirement has no constraint to evaluate)"
    )
    m = project.VERIFY_LINE.search(line)
    assert m is not None
    assert m.group("req") == "MaxPressure"
    assert m.group("verdict") == "undecided"


def test_requirement_construct_excludes_elements_with_no_short_name(tmp_path):
    g = Graph()
    real = URIRef("urn:test:real")
    placeholder = URIRef("urn:test:placeholder")
    g.add((real, RDF.type, SYSML.RequirementUsage))
    g.add((real, TK.declaredShortName, Literal("REQ-001")))
    g.add((placeholder, RDF.type, SYSML.RequirementUsage))  # no declaredShortName

    query = (Path(__file__).parent / "construct-requirements.rq").read_text()
    result = Graph()
    for triple in g.query(query):
        result.add(triple)

    PROJ = Namespace("https://weft.ghostsystems.ai/thread/0.1.0/")
    subjects = {s for s in result.subjects(RDF.type, PROJ.Requirement)}
    assert subjects == {real}


def _claim(g, claim, req, req_name, elem, elem_name):
    g.add((claim, RDF.type, SYSML.SatisfyRequirementUsage))
    g.add((claim, TK.satisfiedRequirement, req))
    g.add((claim, TK.satisfyingFeature, elem))
    g.add((req, TK.declaredName, Literal(req_name)))
    g.add((elem, TK.declaredName, Literal(elem_name)))


def test_two_satisfy_claims_on_one_requirement_each_get_their_own_verdict():
    g = Graph()
    req = URIRef("urn:test:req")
    _claim(g, URIRef("urn:test:claim-pump"), req, "PowerDraw", URIRef("urn:test:pump"), "pump")
    _claim(g, URIRef("urn:test:claim-ctrl"), req, "PowerDraw", URIRef("urn:test:ctrl"), "controller")
    report = "\n".join(
        [
            "m.sysml:1:2  <anonymous> (SatisfyRequirementUsage, satisfies M::PowerDraw by sys.pump): satisfied",
            "m.sysml:2:2  <anonymous> (SatisfyRequirementUsage, satisfies M::PowerDraw by sys.controller): violated",
        ]
    )
    projection = Graph()
    unmatched = project.attach_verdicts(g, projection, report)

    PROJ = Namespace("https://weft.ghostsystems.ai/thread/0.1.0/")
    assert unmatched == []
    assert set(projection.objects(URIRef("urn:test:claim-pump"), PROJ.verdict)) == {Literal("satisfied")}
    assert set(projection.objects(URIRef("urn:test:claim-ctrl"), PROJ.verdict)) == {Literal("violated")}

"""Regression fence for step 6: a class annotated by a metadata definition
must inherit that definition's property shapes onto its own NodeShape (the
derivation decision shacl_export.py documents), and a class with no
annotation must not pick up a stray property shape. Run directly:

    cd spike/shapes && python3 -m pytest test_shacl_export.py
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from rdflib import Graph, SH, URIRef

import shacl_export

BASE = "https://weft.ghostsystems.ai/spike1/test-library/"


def _elements():
    return [
        {"@id": "stereotype", "@type": "MetadataDefinition", "declaredName": "Stamped"},
        {
            "@id": "stereotype-fm",
            "@type": "FeatureMembership",
            "owningType": {"@id": "stereotype"},
            "ownedMemberElement": {"@id": "stamp-feature"},
            "memberName": "stamp",
        },
        {"@id": "stamp-feature", "@type": "ReferenceUsage", "declaredName": "stamp", "type": [{"@id": "stereotype"}]},
        {"@id": "annotated", "@type": "PartDefinition", "declaredName": "Annotated"},
        {"@id": "plain", "@type": "PartDefinition", "declaredName": "Plain"},
        {
            "@id": "md-usage",
            "@type": "MetadataUsage",
            "type": [{"@id": "stereotype"}],
            "annotatedElement": [{"@id": "annotated"}],
        },
    ]


def test_annotated_class_inherits_metadata_property_shape(tmp_path):
    json_path = tmp_path / "in.json"
    json_path.write_text(json.dumps(_elements()))
    out_ttl = tmp_path / "shapes.ttl"
    sys.argv = ["shacl_export.py", str(json_path), BASE, str(out_ttl)]
    shacl_export.main()

    g = Graph()
    g.parse(out_ttl, format="turtle")

    annotated_shape = URIRef(f"{BASE}shape/Annotated")
    plain_shape = URIRef(f"{BASE}shape/Plain")

    annotated_props = set(g.objects(annotated_shape, SH.property))
    plain_props = set(g.objects(plain_shape, SH.property))

    assert len(annotated_props) == 1
    assert plain_props == set()  # Plain carries no metadata, so it inherits nothing


# Spike 2 step 2: non-vacuity for spike/shapes/normative-shapes.ttl (the
# shape set whose sh:targetClass values are the toolkit's own class IRIs,
# not step 5/6's OWL export classes FINDINGS.md found vacuous). Each test
# below injects exactly one violating node for the shape it names and
# asserts a Violation fires, then asserts every shape also has at least
# one focus node on the real pump-system normative graph -- a shape that
# validates cleanly only because it targets nothing would pass the first
# assertion trivially and fail the second, same failure mode FINDINGS.md
# already recorded once.
import pyshacl

NORMATIVE_SHAPES = Path(__file__).parent / "normative-shapes.ttl"
NORMATIVE_GRAPH = Path(__file__).parent.parent / "normative" / "output" / "pump-system.ttl"

TK = "https://weft.ghostsystems.ai/spike1/toolkit-vocab#"
SYSML_NS = "https://www.omg.org/spec/SysML/20250201/"


def _load_normative_shapes():
    return Graph().parse(NORMATIVE_SHAPES, format="turtle")


def _focus_nodes(report_graph):
    return set(report_graph.objects(None, SH.focusNode))


def test_every_normative_shape_has_a_focus_node_on_the_pump_system_graph():
    data = Graph().parse(NORMATIVE_GRAPH, format="turtle")
    shapes = _load_normative_shapes()
    for shape_name in (
        "ComponentBearerMinCountShape",
        "BearerValueAlignmentAxiomShape",
        "IndividualInterfaceLinkedToSpecificationShape",
    ):
        shape = URIRef(f"https://weft.ghostsystems.ai/spike2/normative-shapes/{shape_name}")
        target_class = shapes.value(shape, SH.targetClass)
        assert (None, URIRef("http://www.w3.org/1999/02/22-rdf-syntax-ns#type"), target_class) in data, (
            f"{shape_name}'s target class {target_class} has no instance in the pump-system "
            "normative graph -- the shape would validate vacuously (the FINDINGS.md failure mode)"
        )


def test_component_bearer_min_count_shape_catches_a_component_with_no_bearer_value():
    data = Graph().parse(
        data=f"""
        @prefix sysml: <{SYSML_NS}> .
        @prefix tk: <{TK}> .
        <urn:test/md-usage> a sysml:MetadataUsage ;
            tk:metadataDefinition <urn:test/component-def> .
        <urn:test/component-def> tk:declaredName "Component" .
        """,
        format="turtle",
    )
    shapes = _load_normative_shapes()
    conforms, report_graph, _ = pyshacl.validate(data, shacl_graph=shapes, advanced=True)
    assert conforms is False
    assert URIRef("urn:test/md-usage") in _focus_nodes(report_graph)


def test_bearer_value_alignment_axiom_shape_catches_an_unregistered_bearer_value():
    data = Graph().parse(
        data=f"""
        @prefix sysml: <{SYSML_NS}> .
        @prefix tk: <{TK}> .
        <urn:test/unregistered-value> a sysml:AttributeUsage ;
            tk:declaredName "notInTheRegistry" ;
            tk:type <urn:test/bearer-kind> .
        <urn:test/bearer-kind> tk:declaredName "BearerKind" .
        """,
        format="turtle",
    )
    shapes = _load_normative_shapes()
    conforms, report_graph, _ = pyshacl.validate(data, shacl_graph=shapes, advanced=True)
    assert conforms is False
    assert URIRef("urn:test/unregistered-value") in _focus_nodes(report_graph)


def test_individual_interface_shape_catches_an_individual_def_with_no_specialization():
    data = Graph().parse(
        data=f"""
        @prefix sysml: <{SYSML_NS}> .
        @prefix tk: <{TK}> .
        <urn:test/orphan-individual> a sysml:InterfaceDefinition ;
            tk:isIndividual true .
        """,
        format="turtle",
    )
    shapes = _load_normative_shapes()
    conforms, report_graph, _ = pyshacl.validate(data, shacl_graph=shapes, advanced=True)
    assert conforms is False
    assert URIRef("urn:test/orphan-individual") in _focus_nodes(report_graph)


def test_normative_shapes_conform_on_the_real_pump_system_model():
    """AGENTS.md rule 7: every property these shapes require at Violation
    severity is producible through the primary authoring path. The real
    pump-system normative graph is derived from spike/model/*.sysml textual
    notation (sysmlv2 convert), so a clean conforms here on the real model
    -- not a synthetic fixture -- is the rule 7 proof: the bearer values,
    the project-declared value, the two-valued bearer, and the individual
    interface specialization all came from `sysmlv2 check`-passing text.
    """
    data = Graph().parse(NORMATIVE_GRAPH, format="turtle")
    shapes = _load_normative_shapes()
    conforms, _, report_text = pyshacl.validate(data, shacl_graph=shapes, advanced=True)
    assert conforms is True, report_text

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


def test_declared_multiplicity_sets_the_property_shape_cardinality(tmp_path):
    """Decision 0005's `bearer : BearerKind[1..*]` gives sh:minCount 1 and no
    sh:maxCount, so a two-valued bearer conforms; a feature with no declared
    multiplicity keeps exactly one."""
    elements = [
        {"@id": "bk", "@type": "AttributeDefinition", "declaredName": "BearerKind"},
        {"@id": "comp", "@type": "MetadataDefinition", "declaredName": "Component"},
        {
            "@id": "fm",
            "@type": "FeatureMembership",
            "owningType": {"@id": "comp"},
            "ownedMemberElement": {"@id": "bearer"},
            "memberName": "bearer",
        },
        {
            "@id": "bearer",
            "@type": "AttributeUsage",
            "declaredName": "bearer",
            "type": [{"@id": "bk"}],
            "multiplicity": {"@id": "mult"},
        },
        {"@id": "mult", "@type": "MultiplicityRange", "lowerBound": {"@id": "lo"}, "upperBound": {"@id": "hi"}},
        {"@id": "lo", "@type": "LiteralInteger", "value": 1},
        {"@id": "hi", "@type": "LiteralInfinity"},
        {"@id": "part", "@type": "PartDefinition", "declaredName": "Part"},
        {
            "@id": "fm2",
            "@type": "FeatureMembership",
            "owningType": {"@id": "part"},
            "ownedMemberElement": {"@id": "kind"},
            "memberName": "kind",
        },
        {"@id": "kind", "@type": "AttributeUsage", "declaredName": "kind", "type": [{"@id": "bk"}]},
    ]
    json_path = tmp_path / "in.json"
    json_path.write_text(json.dumps(elements))
    out_ttl = tmp_path / "shapes.ttl"
    sys.argv = ["shacl_export.py", str(json_path), BASE, str(out_ttl)]
    shacl_export.main()
    g = Graph().parse(out_ttl, format="turtle")

    bearer_shape = URIRef(f"{BASE}property/Component_bearer-shape")
    assert g.value(bearer_shape, SH.minCount).toPython() == 1
    assert g.value(bearer_shape, SH.maxCount) is None
    kind_shape = URIRef(f"{BASE}property/Part_kind-shape")
    assert g.value(kind_shape, SH.minCount).toPython() == 1
    assert g.value(kind_shape, SH.maxCount).toPython() == 1


# Spike 2 step 2: non-vacuity for spike/shapes/normative-shapes.ttl (the
# shape set whose sh:targetClass values are the toolkit's own class IRIs,
# not the step 5/6 OWL export classes that BACKENDS.md found vacuous as the
# normative holon's boundary). The synthetic tests inject one violating
# node per shape and assert a Violation fires. The precondition test
# asserts each shape has a node on the real pump-system normative graph
# that meets its SPARQL precondition, and that breaking that node fires the
# shape; a shape that conforms only because it selects nothing passes the
# synthetic tests and fails the precondition test.
import pyshacl
import pytest
from rdflib import RDF

NORMATIVE_SHAPES = Path(__file__).parent / "normative-shapes.ttl"
NORMATIVE_GRAPH = Path(__file__).parent.parent / "normative" / "output" / "pump-system.ttl"

TK = "https://weft.ghostsystems.ai/spike1/toolkit-vocab#"
SYSML_NS = "https://www.omg.org/spec/SysML/20250201/"


def _load_normative_shapes():
    return Graph().parse(NORMATIVE_SHAPES, format="turtle")


def _focus_nodes(report_graph):
    return set(report_graph.objects(None, SH.focusNode))


_PREFIXES = f"""
PREFIX tk: <{TK}>
PREFIX sysml: <{SYSML_NS}>
"""

# Each shape's SPARQL constraint selects $this only when a precondition
# holds (the MetadataUsage applies Component; the AttributeUsage is a
# BearerKind value other than the `bearer` slot; the InterfaceDefinition is
# `individual`). A node of the target class that fails the precondition is
# never checked, so an instance of the target class is not enough to show
# the shape ran. These queries restate each precondition; the mutation for
# each shape removes or renames what the constraint checks, on the real
# graph, so the test also shows the precondition and the shape select the
# same node.
PRECONDITIONS = {
    "ComponentBearerMinCountShape": (
        """SELECT ?this WHERE {
            ?this a sysml:MetadataUsage ; tk:metadataDefinition ?def .
            ?def tk:declaredName "Component" .
        }""",
        """DELETE { $this tk:ownedFeature ?bf } WHERE {
            $this tk:ownedFeature ?bf . ?bf tk:declaredName "bearer" .
        }""",
    ),
    "BearerValueAlignmentAxiomShape": (
        """SELECT ?this WHERE {
            ?this a sysml:AttributeUsage ; tk:type ?bk ; tk:declaredName ?name .
            ?bk tk:declaredName "BearerKind" .
            FILTER (?name != "bearer")
        }""",
        """DELETE { $this tk:declaredName ?n } INSERT { $this tk:declaredName "unregisteredValue" }
           WHERE { $this tk:declaredName ?n }""",
    ),
    "IndividualInterfaceLinkedToSpecificationShape": (
        """SELECT ?this WHERE {
            ?this a sysml:InterfaceDefinition ; tk:isIndividual true .
        }""",
        """DELETE { $this tk:ownedSpecialization ?s } WHERE { $this tk:ownedSpecialization ?s }""",
    ),
}


def _precondition_nodes(data, shape_name):
    select, _ = PRECONDITIONS[shape_name]
    return sorted({row.this for row in data.query(_PREFIXES + select)}, key=str)


@pytest.mark.parametrize("shape_name", sorted(PRECONDITIONS))
def test_every_normative_shape_has_a_focus_node_meeting_its_precondition(shape_name):
    data = Graph().parse(NORMATIVE_GRAPH, format="turtle")
    shapes = _load_normative_shapes()
    shape = URIRef(f"https://weft.ghostsystems.ai/spike2/normative-shapes/{shape_name}")
    target_class = shapes.value(shape, SH.targetClass)

    nodes = _precondition_nodes(data, shape_name)
    assert nodes, (
        f"no node in the pump-system normative graph meets {shape_name}'s SPARQL precondition; "
        "the shape would validate vacuously (the BACKENDS.md failure mode)"
    )
    for node in nodes:
        assert (node, RDF.type, target_class) in data

    # The real graph conforms (test below), so each precondition node passed
    # the constraint. Breaking the checked part on the first such node must
    # make that node a focus node of a Violation from this shape.
    _, mutation = PRECONDITIONS[shape_name]
    data.update(_PREFIXES + mutation.replace("$this", f"<{nodes[0]}>"))
    conforms, report_graph, _ = pyshacl.validate(data, shacl_graph=shapes, advanced=True)
    assert conforms is False
    fired = {
        report_graph.value(r, SH.focusNode)
        for r in report_graph.subjects(SH.sourceShape, shape)
    }
    assert nodes[0] in fired


def test_component_bearer_shape_precondition_covers_a_two_valued_bearer():
    """The `(tk:member|tk:argument)*` part of the min-count path is exercised
    by EmbeddedController's `bearer = (material, information)`, not only by
    single-valued bearers."""
    data = Graph().parse(NORMATIVE_GRAPH, format="turtle")
    rows = data.query(
        _PREFIXES
        + """SELECT ?this WHERE {
            ?this tk:ownedFeature ?bf . ?bf tk:declaredName "bearer" .
            ?bf (tk:member|tk:argument)* ?x . ?x tk:argument ?arg .
        }"""
    )
    multi = {row.this for row in rows}
    assert multi & set(_precondition_nodes(data, "ComponentBearerMinCountShape"))


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
    (not a synthetic fixture) is the rule 7 proof: the bearer values, the
    project-declared value, the two-valued bearer, and the individual
    interface specialization all came from `sysmlv2 check`-passing text.
    The precondition test above shows each shape's constraint is evaluated
    on at least one of those nodes, so the conformance is not vacuous.
    """
    data = Graph().parse(NORMATIVE_GRAPH, format="turtle")
    shapes = _load_normative_shapes()
    conforms, _, report_text = pyshacl.validate(data, shacl_graph=shapes, advanced=True)
    assert conforms is True, report_text

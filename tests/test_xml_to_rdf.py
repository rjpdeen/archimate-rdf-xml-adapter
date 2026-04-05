from archimate_adapter.dto.model import ElementDTO, ModelDTO, RelationshipDTO
from archimate_adapter.services.xml_to_rdf import (
    ElementTypeRegistry,
    RelationshipTypeRegistry,
    build_canonical_import_sparql,
)


def test_build_canonical_import_sparql_phase1():
    model = ModelDTO()
    model.add_element(
        ElementDTO(
            identifier="app-1",
            xml_type="ApplicationComponent",
            name="My Application",
        )
    )
    model.add_element(
        ElementDTO(
            identifier="actor-1",
            xml_type="BusinessActor",
            name="Actor 1",
        )
    )
    model.add_relationship(
        RelationshipDTO(
            identifier="rel-1",
            xml_type="Serving",
            exchange_type="Serving",
            source_id="app-1",
            target_id="actor-1",
            name="serves",
            documentation="Application serves actor in this model.",
        )
    )

    element_registry = ElementTypeRegistry.from_yaml(
        "src/archimate_adapter/mapping/element_types.yaml"
    )
    relationship_registry = RelationshipTypeRegistry.from_yaml(
        "src/archimate_adapter/mapping/relationship_types.yaml"
    )

    sparql = build_canonical_import_sparql(
        model=model,
        element_registry=element_registry,
        relationship_registry=relationship_registry,
    )

    assert "https://purl.org/archimate#ApplicationComponent" in sparql
    assert "https://purl.org/archimate#BusinessActor" in sparql
    assert "https://purl.org/archimate#serving" in sparql
    assert 'archimate:identifier "rel-1"' in sparql
    assert "<< ex:app-1 <https://purl.org/archimate#serving> ex:actor-1 >>" in sparql

def test_build_canonical_import_sparql_phase1_with_named_graph():
    model = ModelDTO()
    model.add_element(
        ElementDTO(
            identifier="app-1",
            xml_type="ApplicationComponent",
            name="My Application",
        )
    )
    model.add_element(
        ElementDTO(
            identifier="actor-1",
            xml_type="BusinessActor",
            name="Actor 1",
        )
    )
    model.add_relationship(
        RelationshipDTO(
            identifier="rel-1",
            xml_type="Serving",
            exchange_type="Serving",
            source_id="app-1",
            target_id="actor-1",
            name="serves",
            documentation="Application serves actor in this model.",
        )
    )

    element_registry = ElementTypeRegistry.from_yaml(
        "src/archimate_adapter/mapping/element_types.yaml"
    )
    relationship_registry = RelationshipTypeRegistry.from_yaml(
        "src/archimate_adapter/mapping/relationship_types.yaml"
    )

    sparql = build_canonical_import_sparql(
        model=model,
        element_registry=element_registry,
        relationship_registry=relationship_registry,
        graph_iri="https://example.org/graph/test-import",
    )

    assert "INSERT DATA" in sparql
    assert "GRAPH <https://example.org/graph/test-import>" in sparql
    assert "https://purl.org/archimate#ApplicationComponent" in sparql
    assert "https://purl.org/archimate#BusinessActor" in sparql
    assert "https://purl.org/archimate#serving" in sparql
    assert 'archimate:identifier "rel-1"' in sparql
    assert "<< ex:app-1 <https://purl.org/archimate#serving> ex:actor-1 >>" in sparql
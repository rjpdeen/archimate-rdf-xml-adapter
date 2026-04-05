from archimate_adapter.dto.model import ElementDTO, ModelDTO, RelationshipDTO
from archimate_adapter.services.xml_to_rdf import (
    ElementTypeRegistry,
    RelationshipTypeRegistry,
    build_canonical_import_sparql,
)


def test_build_canonical_import_sparql_with_data_object_and_access():
    model = ModelDTO()
    model.add_element(
        ElementDTO(
            identifier="app-1",
            xml_type="ApplicationComponent",
            name="Case App",
            documentation="Application component.",
        )
    )
    model.add_element(
        ElementDTO(
            identifier="data-1",
            xml_type="DataObject",
            name="Case Record",
            documentation="Data object containing case data.",
        )
    )
    model.add_relationship(
        RelationshipDTO(
            identifier="rel-4",
            xml_type="Access",
            exchange_type="Access",
            source_id="app-1",
            target_id="data-1",
            name="accesses",
            documentation="Application component accesses data object.",
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
    assert "https://purl.org/archimate#DataObject" in sparql
    assert "https://purl.org/archimate#access" in sparql
    assert 'archimate:identifier "rel-4"' in sparql
    assert (
        "<< ex:app-1 <https://purl.org/archimate#access> ex:data-1 >>"
        in sparql
    )
    assert (
        "ex:app-1 <https://purl.org/archimate#access> ex:data-1 ."
        in sparql
    )
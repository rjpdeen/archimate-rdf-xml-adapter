from archimate_adapter.dto.model import ElementDTO, ModelDTO, RelationshipDTO
from archimate_adapter.services.xml_to_rdf import (
    ElementTypeRegistry,
    RelationshipTypeRegistry,
    build_canonical_import_sparql,
)


def test_build_canonical_import_sparql_with_application_service_and_realization():
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
            identifier="appsvc-1",
            xml_type="ApplicationService",
            name="Case API",
            documentation="Application service.",
        )
    )
    model.add_relationship(
        RelationshipDTO(
            identifier="rel-3",
            xml_type="Realization",
            exchange_type="Realization",
            source_id="app-1",
            target_id="appsvc-1",
            name="realizes",
            documentation="Application component realizes application service.",
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
    assert "https://purl.org/archimate#ApplicationService" in sparql
    assert "https://purl.org/archimate#realization" in sparql
    assert 'archimate:identifier "rel-3"' in sparql
    assert (
        "<< ex:app-1 <https://purl.org/archimate#realization> ex:appsvc-1 >>"
        in sparql
    )
    assert (
        "ex:app-1 <https://purl.org/archimate#realization> ex:appsvc-1 ."
        in sparql
    )
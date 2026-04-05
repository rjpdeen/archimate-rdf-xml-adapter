from archimate_adapter.dto.model import ElementDTO, ModelDTO, RelationshipDTO
from archimate_adapter.services.xml_to_rdf import (
    ElementTypeRegistry,
    RelationshipTypeRegistry,
    build_canonical_import_sparql,
)


def test_build_canonical_import_sparql_with_business_process_and_assignment():
    model = ModelDTO()
    model.add_element(
        ElementDTO(
            identifier="actor-1",
            xml_type="BusinessActor",
            name="Case Worker",
            documentation="Responsible business actor.",
        )
    )
    model.add_element(
        ElementDTO(
            identifier="process-1",
            xml_type="BusinessProcess",
            name="Handle Application",
            documentation="Business process for handling an application.",
        )
    )
    model.add_relationship(
        RelationshipDTO(
            identifier="rel-2",
            xml_type="Assignment",
            exchange_type="Assignment",
            source_id="actor-1",
            target_id="process-1",
            name="is responsible for",
            documentation="Actor is assigned to process.",
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

    assert "https://purl.org/archimate#BusinessActor" in sparql
    assert "https://purl.org/archimate#BusinessProcess" in sparql
    assert "https://purl.org/archimate#assignment" in sparql
    assert 'archimate:identifier "rel-2"' in sparql
    assert (
        "<< ex:actor-1 <https://purl.org/archimate#assignment> ex:process-1 >>"
        in sparql
    )
    assert (
        "ex:actor-1 <https://purl.org/archimate#assignment> ex:process-1 ."
        in sparql
    )
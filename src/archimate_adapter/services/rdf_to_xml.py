from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

from archimate_adapter.dto.model import ElementDTO, ModelDTO, RelationshipDTO
from archimate_adapter.mapping.iri_registry import identifier_from_iri, relationship_key


@dataclass(slots=True)
class RelationshipTypeRegistry:
    predicate_to_config: dict[str, dict[str, str]]

    @classmethod
    def from_yaml(cls, path: str | Path) -> "RelationshipTypeRegistry":
        with open(path, "r", encoding="utf-8") as handle:
            data = yaml.safe_load(handle) or {}

        rdf_to_xml = data.get("rdf_to_xml", {})
        return cls(predicate_to_config=rdf_to_xml)

    def xml_type_for_predicate(self, predicate_iri: str) -> str:
        try:
            return self.predicate_to_config[predicate_iri]["xml_type"]
        except KeyError as exc:
            raise KeyError(f"No XML type configured for predicate: {predicate_iri}") from exc

    def exchange_type_for_predicate(self, predicate_iri: str) -> str:
        try:
            return self.predicate_to_config[predicate_iri]["exchange_type"]
        except KeyError as exc:
            raise KeyError(f"No exchange type configured for predicate: {predicate_iri}") from exc

    def relationship_predicates(self) -> list[str]:
        return list(self.predicate_to_config.keys())

    def supported_predicate_iris(self) -> list[str]:
        return list(self.predicate_to_config.keys())


@dataclass(slots=True)
class ElementTypeRegistry:
    """
    Registry for mapping canonical RDF classes back to ArchiMate XML element types.
    """

    class_to_config: dict[str, dict[str, str]]

    @classmethod
    def from_yaml(cls, path: str | Path) -> "ElementTypeRegistry":
        with open(path, "r", encoding="utf-8") as handle:
            data = yaml.safe_load(handle) or {}

        rdf_to_xml = data.get("rdf_to_xml", {})
        mapping: dict[str, dict[str, str]] = {}

        for class_iri, config in rdf_to_xml.items():
            xml_type = config.get("xml_type")
            if not xml_type:
                raise ValueError(
                    f"Missing xml_type for class '{class_iri}' in {path}"
                )
            mapping[class_iri] = config

        return cls(class_to_config=mapping)

    def xml_type_for_class(self, class_iri: str) -> str:
        try:
            return self.class_to_config[class_iri]["xml_type"]
        except KeyError as exc:
            raise KeyError(f"No XML type configured for RDF class: {class_iri}") from exc

    def exchange_type_for_class(self, class_iri: str) -> str:
        try:
            config = self.class_to_config[class_iri]
            return config.get("exchange_type", config["xml_type"])
        except KeyError as exc:
            raise KeyError(
                f"No exchange type configured for RDF class: {class_iri}"
            ) from exc


def model_from_sparql_results(
    element_rows: list[dict[str, Any]],
    relationship_rows: list[dict[str, Any]],
    element_registry: ElementTypeRegistry,
    relationship_registry: RelationshipTypeRegistry,
    model_identifier: str = "model-1",
    model_name: str = "Imported model",
    require_relationship_identifier: bool = True,
) -> ModelDTO:
    """
    Build a ModelDTO from SPARQL result rows.

    Expected input:
    - element_rows from select_elements_query()
    - relationship_rows from select_relationships_query()
    """
    model = ModelDTO()

    for row in element_rows:
        element = element_dto_from_row(row, element_registry)
        model.add_element(element)

    seen_relationship_triples: set[tuple[str, str, str]] = set()

    for row in relationship_rows:
        relationship = relationship_dto_from_row(
            row=row,
            relationship_registry=relationship_registry,
            require_identifier=require_relationship_identifier,
        )

        triple_key = relationship_key(
            relationship.source_id,
            _required_str(row, "pred"),
            relationship.target_id,
        )
        if triple_key in seen_relationship_triples:
            raise ValueError(
                "Duplicate canonical relationship triple encountered during RDF -> DTO mapping: "
                f"{triple_key}"
            )
        seen_relationship_triples.add(triple_key)

        model.add_relationship(relationship)

    return model


def element_dto_from_row(
    row: dict[str, Any],
    element_registry: ElementTypeRegistry,
) -> ElementDTO:
    element_iri = _required_str(row, "element")
    rdf_type = _required_str(row, "type")
    identifier = _required_str(row, "id")

    decoded_identifier = identifier_from_iri(element_iri)
    if decoded_identifier != identifier:
        raise ValueError(
            f"Element identifier mismatch between IRI and archimate:identifier: "
            f"{element_iri} vs {identifier}"
        )

    xml_type = element_registry.xml_type_for_class(rdf_type)
    exchange_type = element_registry.exchange_type_for_class(rdf_type)

    # Handle junctions: if it's a Junction, determine XML type from junctionType
    junction_type = _optional_str(row, "junctionType")
    if rdf_type == "https://purl.org/archimate#Junction":
        if junction_type == "and":
            xml_type = "AndJunction"
            exchange_type = "AndJunction"
        elif junction_type == "or":
            xml_type = "OrJunction"
            exchange_type = "OrJunction"
        else:
            raise ValueError(f"Unknown junctionType for Junction element: {junction_type}")

    return ElementDTO(
        identifier=identifier,
        xml_type=xml_type,
        exchange_type=exchange_type,
        name=_optional_str(row, "name"),
        documentation=_optional_str(row, "documentation"),
        junction_type=junction_type,
    )


def relationship_dto_from_row(
    row: dict[str, Any],
    relationship_registry: RelationshipTypeRegistry,
    require_identifier: bool = True,
) -> RelationshipDTO:
    src_iri = _required_str(row, "src")
    pred_iri = _required_str(row, "pred")
    tgt_iri = _required_str(row, "tgt")

    source_id = identifier_from_iri(src_iri)
    target_id = identifier_from_iri(tgt_iri)

    identifier = _optional_str(row, "rid")
    if require_identifier and not identifier:
        raise ValueError(
            "Missing relationship identifier on RDF-star triple metadata "
            f"for ({src_iri}, {pred_iri}, {tgt_iri})"
        )

    return RelationshipDTO(
        identifier=identifier or _synthetic_relationship_id(source_id, pred_iri, target_id),
        xml_type=relationship_registry.xml_type_for_predicate(pred_iri),
        exchange_type=relationship_registry.exchange_type_for_predicate(pred_iri),
        source_id=source_id,
        target_id=target_id,
        name=_optional_str(row, "rname"),
        documentation=_optional_str(row, "rdocumentation"),
    )


def _synthetic_relationship_id(source_id: str, predicate_iri: str, target_id: str) -> str:
    iri = predicate_iri.rstrip("/#")
    tail = iri.rsplit("#", 1)[-1].rsplit("/", 1)[-1]
    return f"{source_id}--{tail}--{target_id}"


def _required_str(row: dict[str, Any], key: str) -> str:
    value = row.get(key)
    if value is None or value == "":
        raise ValueError(f"Missing required SPARQL field: {key}")
    return str(value)


def _optional_str(row: dict[str, Any], key: str) -> str | None:
    value = row.get(key)
    if value is None or value == "":
        return None
    return str(value)
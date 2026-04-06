from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import yaml


@dataclass(slots=True)
class ElementTypeRegistry:
    rdf_to_xml_map: dict[str, dict[str, str]]
    xml_to_rdf_map: dict[str, dict[str, str]]

    @classmethod
    def from_yaml(cls, path: str | Path) -> "ElementTypeRegistry":
        with open(path, "r", encoding="utf-8") as handle:
            data = yaml.safe_load(handle) or {}

        return cls(
            rdf_to_xml_map=data.get("rdf_to_xml", {}),
            xml_to_rdf_map=data.get("xml_to_rdf", {}),
        )

    def xml_type_for_class(self, rdf_class_iri: str) -> str:
        try:
            return self.rdf_to_xml_map[rdf_class_iri]["xml_type"]
        except KeyError as exc:
            raise KeyError(f"No XML type configured for RDF class: {rdf_class_iri}") from exc

    def exchange_type_for_class(self, rdf_class_iri: str) -> str:
        try:
            config = self.rdf_to_xml_map[rdf_class_iri]
            return config.get("exchange_type", config["xml_type"])
        except KeyError as exc:
            raise KeyError(
                f"No exchange type configured for RDF class: {rdf_class_iri}"
            ) from exc

    def rdf_class_for_xml_type(self, xml_type: str) -> str:
        try:
            return self.xml_to_rdf_map[xml_type]["rdf_class"]
        except KeyError as exc:
            raise KeyError(f"No RDF class configured for XML type: {xml_type}") from exc


@dataclass(slots=True)
class RelationshipTypeRegistry:
    rdf_to_xml_map: dict[str, dict[str, str]]
    xml_to_rdf_map: dict[str, dict[str, str]]

    @classmethod
    def from_yaml(cls, path: str | Path) -> "RelationshipTypeRegistry":
        with open(path, "r", encoding="utf-8") as handle:
            data = yaml.safe_load(handle) or {}

        return cls(
            rdf_to_xml_map=data.get("rdf_to_xml", {}),
            xml_to_rdf_map=data.get("xml_to_rdf", {}),
        )

    def xml_type_for_predicate(self, rdf_predicate_iri: str) -> str:
        try:
            return self.rdf_to_xml_map[rdf_predicate_iri]["xml_type"]
        except KeyError as exc:
            raise KeyError(
                f"No XML relationship type configured for RDF predicate: {rdf_predicate_iri}"
            ) from exc

    def exchange_type_for_predicate(self, rdf_predicate_iri: str) -> str:
        try:
            return self.rdf_to_xml_map[rdf_predicate_iri]["exchange_type"]
        except KeyError as exc:
            raise KeyError(
                f"No exchange type configured for RDF predicate: {rdf_predicate_iri}"
            ) from exc

    def rdf_predicate_for_xml_type(self, xml_type: str) -> str:
        try:
            return self.xml_to_rdf_map[xml_type]["rdf_predicate"]
        except KeyError as exc:
            raise KeyError(
                f"No RDF predicate configured for XML relationship type: {xml_type}"
            ) from exc

    def supported_predicate_iris(self) -> list[str]:
        return list(self.rdf_to_xml_map.keys())
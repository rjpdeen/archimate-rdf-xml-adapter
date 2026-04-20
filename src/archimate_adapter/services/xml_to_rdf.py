from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import yaml

from archimate_adapter.dto.model import ElementDTO, ModelDTO, RelationshipDTO
from archimate_adapter.namespaces import ARCHIMATE_NS, DCT_NS, EX_NS, RDF_NS


class XmlToRdfError(ValueError):
    pass


@dataclass(slots=True)
class ElementTypeRegistry:
    xml_to_config: dict[str, dict[str, str]]

    @classmethod
    def from_yaml(cls, path: str | Path) -> "ElementTypeRegistry":
        with open(path, "r", encoding="utf-8") as handle:
            data = yaml.safe_load(handle) or {}

        xml_to_rdf = data.get("xml_to_rdf", {})
        mapping: dict[str, dict[str, str]] = {}

        for xml_type, config in xml_to_rdf.items():
            rdf_class = config.get("rdf_class")
            if not rdf_class:
                raise ValueError(
                    f"Missing rdf_class for xml type '{xml_type}' in {path}"
                )
            mapping[xml_type] = config

        return cls(xml_to_config=mapping)

    def rdf_class_for_xml_type(self, xml_type: str) -> str:
        try:
            return self.xml_to_config[xml_type]["rdf_class"]
        except KeyError as exc:
            raise KeyError(f"No RDF class configured for XML type: {xml_type}") from exc

    def junction_type_for_xml_type(self, xml_type: str) -> str | None:
        try:
            return self.xml_to_config[xml_type].get("junction_type")
        except KeyError:
            return None

    def supported_element_type_iris(self) -> list[str]:
        return [config["rdf_class"] for config in self.xml_to_config.values()]


@dataclass(slots=True)
class RelationshipTypeRegistry:
    xml_to_config: dict[str, dict[str, str]]

    @classmethod
    def from_yaml(cls, path: str | Path) -> "RelationshipTypeRegistry":
        with open(path, "r", encoding="utf-8") as handle:
            data = yaml.safe_load(handle) or {}

        xml_to_rdf = data.get("xml_to_rdf", {})
        return cls(xml_to_config=xml_to_rdf)

    def rdf_predicate_for_xml_type(self, xml_type: str) -> str:
        try:
            return self.xml_to_config[xml_type]["rdf_predicate"]
        except KeyError as exc:
            raise KeyError(f"No RDF predicate configured for XML type: {xml_type}") from exc
    
    def supported_predicate_iris(self) -> list[str]:
        return [
            config["rdf_predicate"]
            for config in self.xml_to_config.values()
            if "rdf_predicate" in config
        ]


def build_canonical_import_sparql(
    model: ModelDTO,
    element_registry: ElementTypeRegistry,
    relationship_registry: RelationshipTypeRegistry,
    graph_iri: str | None = None,
) -> str:
    lines: list[str] = [
        f"PREFIX rdf: <{RDF_NS}>",
        f"PREFIX archimate: <{ARCHIMATE_NS}>",
        f"PREFIX dct: <{DCT_NS}>",
        f"PREFIX ex: <{EX_NS}>",
        "",
        "INSERT DATA {",
    ]

    if graph_iri:
        lines.append(f"  GRAPH <{graph_iri}> {{")

    indent = "    " if graph_iri else ""

    for element in model.elements:
        lines.extend(_element_block(element, element_registry, indent=indent))

    for relationship in model.relationships:
        lines.extend(
            _relationship_block(
                relationship,
                relationship_registry,
                indent=indent,
            )
        )

    if graph_iri:
        lines.append("  }")

    lines.append("}")
    return "\n".join(lines)


def _element_block(
    element: ElementDTO,
    element_registry: ElementTypeRegistry,
    indent: str = "",
) -> list[str]:
    rdf_class = element_registry.rdf_class_for_xml_type(element.xml_type)
    subject = _ex(element.identifier)

    lines: list[str] = [
        f"{indent}{subject} rdf:type <{rdf_class}> ;",
        f'{indent}  archimate:identifier "{_escape_string(element.identifier)}"',
    ]

    if element.name:
        lines[-1] += " ;"
        lines.append(f'{indent}  archimate:name "{_escape_string(element.name)}"@en')

    if element.documentation:
        lines[-1] += " ;"
        lines.append(
            f'{indent}  dct:description "{_escape_string(element.documentation)}"@en'
        )

    if element.junction_type:
        lines[-1] += " ;"
        lines.append(f'{indent}  archimate:junctionType "{_escape_string(element.junction_type)}"')

    lines[-1] += " ."
    return lines + [""]


def _relationship_block(
    relationship: RelationshipDTO,
    relationship_registry: RelationshipTypeRegistry,
    indent: str = "",
) -> list[str]:
    rdf_predicate = relationship_registry.rdf_predicate_for_xml_type(
        relationship.xml_type
    )

    source = _ex(relationship.source_id)
    target = _ex(relationship.target_id)
    predicate = f"<{rdf_predicate}>"
    quoted = f"<< {source} {predicate} {target} >>"

    lines: list[str] = [
        f"{indent}{source} {predicate} {target} .",
        "",
        f'{indent}{quoted} archimate:identifier "{_escape_string(relationship.identifier)}"',
    ]

    if relationship.name:
        lines[-1] += " ;"
        lines.append(f'{indent}  archimate:name "{_escape_string(relationship.name)}"@en')

    if relationship.documentation:
        lines[-1] += " ;"
        lines.append(
            f'{indent}  dct:description "{_escape_string(relationship.documentation)}"@en'
        )

    lines[-1] += " ."
    return lines + [""]


def _ex(identifier: str) -> str:
    if not identifier or not identifier.strip():
        raise XmlToRdfError("Identifier must not be empty.")
    return f"ex:{identifier.strip()}"


def _escape_string(value: str) -> str:
    return (
        value.replace("\\", "\\\\")
        .replace('"', '\\"')
        .replace("\n", "\\n")
        .replace("\r", "\\r")
    )
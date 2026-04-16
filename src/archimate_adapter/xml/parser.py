from __future__ import annotations

from pathlib import Path
import xml.etree.ElementTree as ET

from archimate_adapter.dto.model import ElementDTO, RelationshipDTO, ModelDTO
from archimate_adapter.services.xml_to_rdf import (
    ElementTypeRegistry,
    RelationshipTypeRegistry,
)


ARCHIMATE_NS = "http://www.opengroup.org/xsd/archimate/3.0/"
XSI_NS = "http://www.w3.org/2001/XMLSchema-instance"

NS = {
    "a": ARCHIMATE_NS,
    "xsi": XSI_NS,
}

ELEMENT_MAPPING_PATH = Path(__file__).resolve().parents[1] / "mapping" / "element_types.yaml"
RELATIONSHIP_MAPPING_PATH = Path(__file__).resolve().parents[1] / "mapping" / "relationship_types.yaml"

ELEMENT_REGISTRY = ElementTypeRegistry.from_yaml(ELEMENT_MAPPING_PATH)
RELATIONSHIP_REGISTRY = RelationshipTypeRegistry.from_yaml(RELATIONSHIP_MAPPING_PATH)


class ArchimateXmlParseError(ValueError):
    pass


def parse_archimate_model(path: str | Path) -> ModelDTO:
    tree = ET.parse(path)
    root = tree.getroot()
    return parse_archimate_model_root(root)


def parse_archimate_model_string(xml_text: str) -> ModelDTO:
    root = ET.fromstring(xml_text)
    return parse_archimate_model_root(root)


def parse_archimate_model_root(root: ET.Element) -> ModelDTO:
    _assert_is_model_root(root)

    model = ModelDTO()

    elements_parent = root.find("a:elements", NS)
    if elements_parent is not None:
        for element_el in elements_parent.findall("a:element", NS):
            model.add_element(_parse_element(element_el))

    relationships_parent = root.find("a:relationships", NS)
    if relationships_parent is not None:
        for rel_el in relationships_parent.findall("a:relationship", NS):
            model.add_relationship(_parse_relationship(rel_el))

    return model


def _assert_is_model_root(root: ET.Element) -> None:
    expected_tag = f"{{{ARCHIMATE_NS}}}model"
    if root.tag != expected_tag:
        raise ArchimateXmlParseError(
            f"Expected root tag '{expected_tag}', got '{root.tag}'."
        )

    version = root.get("version")
    if version != "1.0":
        raise ArchimateXmlParseError(
            f"Expected ArchiMate Exchange XML version '1.0', got '{version}'."
        )


def _parse_element(element_el: ET.Element) -> ElementDTO:
    identifier = _required_attr(element_el, "identifier")
    xml_type = _required_xsi_type(element_el)

    if xml_type not in ELEMENT_REGISTRY.xml_to_class:
        raise ArchimateXmlParseError(
            f"Unsupported element xsi:type '{xml_type}' for element '{identifier}'."
        )

    return ElementDTO(
        identifier=identifier,
        xml_type=xml_type,
        name=_parse_text_child(element_el, "name"),
        documentation=_parse_text_child(element_el, "documentation"),
    )


def _parse_relationship(rel_el: ET.Element) -> RelationshipDTO:
    identifier = _required_attr(rel_el, "identifier")
    xml_type = _required_xsi_type(rel_el)

    if xml_type not in RELATIONSHIP_REGISTRY.xml_to_config:
        raise ArchimateXmlParseError(
            f"Unsupported relationship xsi:type '{xml_type}' for relationship '{identifier}'."
        )

    source_id = _required_attr(rel_el, "source")
    target_id = _required_attr(rel_el, "target")

    return RelationshipDTO(
        identifier=identifier,
        xml_type=xml_type,
        exchange_type=xml_type,
        source_id=source_id,
        target_id=target_id,
        name=_parse_text_child(rel_el, "name"),
        documentation=_parse_text_child(rel_el, "documentation"),
    )


def _required_attr(el: ET.Element, attr_name: str) -> str:
    value = el.get(attr_name)
    if value is None:
        raise ArchimateXmlParseError(
            f"Missing required attribute '{attr_name}' on element '{el.tag}'."
        )

    value = value.strip()
    if not value:
        raise ArchimateXmlParseError(
            f"Empty required attribute '{attr_name}' on element '{el.tag}'."
        )
    return value


def _required_xsi_type(el: ET.Element) -> str:
    value = el.get(f"{{{XSI_NS}}}type")
    if value is None:
        raise ArchimateXmlParseError(
            f"Missing required xsi:type on element '{el.tag}'."
        )

    value = value.strip()
    if not value:
        raise ArchimateXmlParseError(
            f"Empty required xsi:type on element '{el.tag}'."
        )

    if ":" in value:
        _, local_name = value.split(":", 1)
        return local_name

    return value


def _parse_text_child(parent: ET.Element, local_name: str) -> str | None:
    child = parent.find(f"a:{local_name}", NS)
    if child is None or child.text is None:
        return None

    text = child.text.strip()
    return text or None
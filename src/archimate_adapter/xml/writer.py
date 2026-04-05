from __future__ import annotations

from pathlib import Path
from xml.etree.ElementTree import Element, ElementTree, SubElement, register_namespace

from archimate_adapter.dto.model import ElementDTO, ModelDTO, RelationshipDTO


ARCHIMATE_NS = "http://www.opengroup.org/xsd/archimate/3.0/"
XSI_NS = "http://www.w3.org/2001/XMLSchema-instance"
XML_NS = "http://www.w3.org/XML/1998/namespace"

NSMAP = {
    "": ARCHIMATE_NS,
    "xsi": XSI_NS,
}


def write_model(
    model: ModelDTO,
    output_path: str | Path,
    model_identifier: str = "model-1",
    model_name: str = "ArchiMate Model",
    model_documentation: str | None = None,
) -> None:
    root = model_to_xml_element(
        model=model,
        model_identifier=model_identifier,
        model_name=model_name,
        model_documentation=model_documentation,
    )
    tree = ElementTree(root)

    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    tree.write(output, encoding="utf-8", xml_declaration=True)


def model_to_xml_element(
    model: ModelDTO,
    model_identifier: str = "model-1",
    model_name: str = "ArchiMate Model",
    model_documentation: str | None = None,
) -> Element:
    _register_namespaces()

    root = Element(_qname(ARCHIMATE_NS, "model"))
    root.set("identifier", model_identifier)
    root.set("version", "1.0")
    root.set(
        _qname(XSI_NS, "schemaLocation"),
        f"{ARCHIMATE_NS} http://www.opengroup.org/xsd/archimate/3.1/archimate3_Model.xsd",
    )

    name_el = SubElement(root, _qname(ARCHIMATE_NS, "name"))
    name_el.set(_qname(XML_NS, "lang"), "en")
    name_el.text = model_name

    if model_documentation:
        doc_el = SubElement(root, _qname(ARCHIMATE_NS, "documentation"))
        doc_el.set(_qname(XML_NS, "lang"), "en")
        doc_el.text = model_documentation

    elements_el = SubElement(root, _qname(ARCHIMATE_NS, "elements"))
    for element in model.elements:
        elements_el.append(_element_to_xml(element))

    relationships_el = SubElement(root, _qname(ARCHIMATE_NS, "relationships"))
    for relationship in model.relationships:
        relationships_el.append(_relationship_to_xml(relationship))

    return root


def _element_to_xml(element: ElementDTO) -> Element:
    el = Element(_qname(ARCHIMATE_NS, "element"))
    el.set("identifier", element.identifier)

    exchange_type = getattr(element, "exchange_type", None) or element.xml_type
    el.set(_qname(XSI_NS, "type"), exchange_type)

    if element.name:
        name_el = SubElement(el, _qname(ARCHIMATE_NS, "name"))
        name_el.set(_qname(XML_NS, "lang"), "en")
        name_el.text = element.name

    if element.documentation:
        doc_el = SubElement(el, _qname(ARCHIMATE_NS, "documentation"))
        doc_el.set(_qname(XML_NS, "lang"), "en")
        doc_el.text = element.documentation

    return el


def _relationship_to_xml(relationship: RelationshipDTO) -> Element:
    el = Element(_qname(ARCHIMATE_NS, "relationship"))
    el.set("identifier", relationship.identifier)
    el.set("source", relationship.source_id)
    el.set("target", relationship.target_id)

    exchange_type = relationship.exchange_type or relationship.xml_type
    el.set(_qname(XSI_NS, "type"), exchange_type)

    if relationship.name:
        name_el = SubElement(el, _qname(ARCHIMATE_NS, "name"))
        name_el.set(_qname(XML_NS, "lang"), "en")
        name_el.text = relationship.name

    if relationship.documentation:
        doc_el = SubElement(el, _qname(ARCHIMATE_NS, "documentation"))
        doc_el.set(_qname(XML_NS, "lang"), "en")
        doc_el.text = relationship.documentation

    return el


def _register_namespaces() -> None:
    for prefix, uri in NSMAP.items():
        register_namespace(prefix, uri)


def _qname(namespace: str, local_name: str) -> str:
    return f"{{{namespace}}}{local_name}"
from dataclasses import dataclass, field
from typing import Optional, List


@dataclass(slots=True)
class ElementDTO:
    identifier: str
    xml_type: str
    name: Optional[str] = None
    documentation: Optional[str] = None
    exchange_type: Optional[str] = None


@dataclass(slots=True)
class RelationshipDTO:
    identifier: str
    xml_type: str
    source_id: str
    target_id: str
    name: Optional[str] = None
    documentation: Optional[str] = None
    exchange_type: Optional[str] = None


@dataclass(slots=True)
class ModelDTO:
    """
    Neutral in-memory model container used between the XML layer and the RDF layer.
    """

    elements: List[ElementDTO] = field(default_factory=list)
    relationships: List[RelationshipDTO] = field(default_factory=list)

    def get_element(self, identifier: str) -> ElementDTO:
        for element in self.elements:
            if element.identifier == identifier:
                return element
        raise KeyError(f"Element not found: {identifier}")

    def has_element(self, identifier: str) -> bool:
        return any(element.identifier == identifier for element in self.elements)

    def add_element(self, element: ElementDTO) -> None:
        if self.has_element(element.identifier):
            raise ValueError(f"Duplicate element identifier: {element.identifier}")
        self.elements.append(element)

    def add_relationship(self, relationship: RelationshipDTO) -> None:
        if not self.has_element(relationship.source_id):
            raise ValueError(
                f"Relationship source does not exist in model: {relationship.source_id}"
            )
        if not self.has_element(relationship.target_id):
            raise ValueError(
                f"Relationship target does not exist in model: {relationship.target_id}"
            )
        if any(r.identifier == relationship.identifier for r in self.relationships):
            raise ValueError(
                f"Duplicate relationship identifier: {relationship.identifier}"
            )
        self.relationships.append(relationship)
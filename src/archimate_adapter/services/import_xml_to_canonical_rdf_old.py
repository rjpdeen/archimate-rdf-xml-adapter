from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from archimate_adapter.graphdb.client import GraphDBClient
from archimate_adapter.services.assert_canonical_graph_integrity import (
    AssertCanonicalGraphIntegrityService,
)
from archimate_adapter.services.xml_to_rdf import (
    ElementTypeRegistry,
    RelationshipTypeRegistry,
    build_canonical_import_sparql,
)
from archimate_adapter.xml.parser import parse_archimate_model


@dataclass
class ImportXmlToCanonicalRdfService:
    graphdb_base_url: str
    repository_id: str
    element_mapping_path: str
    relationship_mapping_path: str
    graph_iri: str | None = None
    replace_graph: bool = False

    def import_from_file(self, xml_path: str | Path) -> None:
        model = parse_archimate_model(xml_path)

        element_registry = ElementTypeRegistry.from_yaml(self.element_mapping_path)
        relationship_registry = RelationshipTypeRegistry.from_yaml(
            self.relationship_mapping_path
        )

        sparql = build_canonical_import_sparql(
            model=model,
            element_registry=element_registry,
            relationship_registry=relationship_registry,
            graph_iri=self.graph_iri,
        )

        client = GraphDBClient(
            base_url=self.graphdb_base_url,
            repository_id=self.repository_id,
        )

        if self.replace_graph:
            if not self.graph_iri:
                raise ValueError("replace_graph=True requires graph_iri to be set")
            client.update(f"CLEAR GRAPH <{self.graph_iri}>")

        client.update(sparql)

        integrity_service = AssertCanonicalGraphIntegrityService(
            client,
            element_registry=element_registry,
            relationship_registry=relationship_registry,
        )
        integrity_service.assert_graph_is_valid(self._require_graph_iri())

    def _require_graph_iri(self) -> str:
        if not self.graph_iri:
            raise ValueError(
                "graph_iri must be set for phase-1 canonical import validation"
            )
        return self.graph_iri
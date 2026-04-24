from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from urllib.parse import quote

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
    graph_target_strategy: str = "single"
    per_file_graph_base_iri: str | None = None

    def import_from_file(self, xml_path: str | Path) -> str:
        xml_path = Path(xml_path)
        target_graph_iri = self.resolve_graph_iri(xml_path)

        model = parse_archimate_model(xml_path)

        element_registry = ElementTypeRegistry.from_yaml(self.element_mapping_path)
        relationship_registry = RelationshipTypeRegistry.from_yaml(
            self.relationship_mapping_path
        )

        sparql = build_canonical_import_sparql(
            model=model,
            element_registry=element_registry,
            relationship_registry=relationship_registry,
            graph_iri=target_graph_iri,
        )

        client = GraphDBClient(
            base_url=self.graphdb_base_url,
            repository_id=self.repository_id,
        )

        if self.replace_graph:
            client.clear_graph(target_graph_iri)

        client.update(sparql)

        integrity_service = AssertCanonicalGraphIntegrityService(
            client,
            element_registry=element_registry,
            relationship_registry=relationship_registry,
        )
        integrity_service.assert_graph_is_valid(target_graph_iri)
        return target_graph_iri

    def resolve_graph_iri(self, xml_path: str | Path) -> str:
        xml_path = Path(xml_path)

        if self.graph_target_strategy == "single":
            if not self.graph_iri:
                raise ValueError(
                    "graph_iri must be set when graph_target_strategy='single'"
                )
            return self.graph_iri

        if self.graph_target_strategy == "per_file":
            base_iri = self.per_file_graph_base_iri or self.graph_iri
            if not base_iri:
                raise ValueError(
                    "per_file graph targeting requires per_file_graph_base_iri or graph_iri"
                )
            return self._build_per_file_graph_iri(base_iri, xml_path)

        raise ValueError(
            f"Unsupported graph_target_strategy: {self.graph_target_strategy}"
        )

    @staticmethod
    def _build_per_file_graph_iri(base_iri: str, xml_path: Path) -> str:
        file_stem = xml_path.stem.strip()
        if not file_stem:
            raise ValueError("Cannot derive per-file graph IRI from an empty file name")
        encoded_stem = quote(file_stem, safe="")
        return f"{base_iri.rstrip('/')}/{encoded_stem}"

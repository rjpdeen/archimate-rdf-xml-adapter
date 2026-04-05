from __future__ import annotations

from dataclasses import dataclass

from archimate_adapter.graphdb.client import GraphDBClient
from archimate_adapter.graphdb.export_queries import (
    select_elements_query,
    select_relationships_query,
)
from archimate_adapter.mapping.registry import (
    ElementTypeRegistry,
    RelationshipTypeRegistry,
)
from archimate_adapter.services.assert_canonical_graph_integrity import (
    AssertCanonicalGraphIntegrityService,
)
from archimate_adapter.services.rdf_to_xml import model_from_sparql_results
from archimate_adapter.xml.writer import write_model


@dataclass
class ExportCanonicalRdfToXmlService:
    graphdb_base_url: str
    repository_id: str
    element_mapping_path: str
    relationship_mapping_path: str
    graph_iri: str | None = None

    def export_to_file(
        self,
        output_path: str,
        model_identifier: str = "model-1",
        model_name: str = "Imported model",
    ) -> None:
        model = self.export_model(
            model_identifier=model_identifier,
            model_name=model_name,
        )
        write_model(model, output_path)

    def export_model(
        self,
        model_identifier: str = "model-1",
        model_name: str = "Imported model",
    ):
        element_registry = ElementTypeRegistry.from_yaml(self.element_mapping_path)
        relationship_registry = RelationshipTypeRegistry.from_yaml(
            self.relationship_mapping_path
        )

        client = GraphDBClient(
            base_url=self.graphdb_base_url,
            repository_id=self.repository_id,
        )

        integrity_service = AssertCanonicalGraphIntegrityService(
            client,
            element_registry=element_registry,
            relationship_registry=relationship_registry,
        )
        integrity_service.assert_graph_is_valid(self._require_graph_iri())

        element_rows = client.select(
            select_elements_query(graph_iri=self.graph_iri)
        )
        relationship_rows = client.select(
            select_relationships_query(
                predicate_iris=relationship_registry.supported_predicate_iris(),
                graph_iri=self.graph_iri,
            )
        )

        return model_from_sparql_results(
            element_rows=element_rows,
            relationship_rows=relationship_rows,
            element_registry=element_registry,
            relationship_registry=relationship_registry,
            model_identifier=model_identifier,
            model_name=model_name,
        )

    def _require_graph_iri(self) -> str:
        if not self.graph_iri:
            raise ValueError(
                "ExportCanonicalRdfToXmlService requires graph_iri for phase 1 "
                "canonical export integrity validation."
            )
        return self.graph_iri
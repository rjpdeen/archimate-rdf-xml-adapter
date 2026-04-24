from __future__ import annotations

from pathlib import Path
from uuid import uuid4

import pytest

from archimate_adapter.config import GRAPHDB_BASE_URL, GRAPHDB_REPOSITORY_ID
from archimate_adapter.graphdb.client import GraphDBClient, GraphDBClientError
from archimate_adapter.services.import_xml_to_canonical_rdf import (
    ImportXmlToCanonicalRdfService,
)


pytestmark = pytest.mark.integration


def _project_root() -> Path:
    return Path(__file__).resolve().parents[1]


def _fixture_xml_files() -> list[Path]:
    fixtures_dir = _project_root() / "tests" / "fixtures" / "xml"
    files = sorted(fixtures_dir.glob("*.xml"))
    if len(files) < 2:
        pytest.skip(
            f"Need at least 2 XML fixtures in {fixtures_dir}, found {len(files)}"
        )
    return files


def _graphdb_client() -> GraphDBClient:
    client = GraphDBClient(
        base_url=GRAPHDB_BASE_URL,
        repository_id=GRAPHDB_REPOSITORY_ID,
        timeout_seconds=10,
    )
    try:
        client.ask("ASK { ?s ?p ?o }")
    except Exception as exc:  # pragma: no cover - skip path depends on local env
        pytest.skip(
            "GraphDB repository is not reachable. "
            f"Expected {GRAPHDB_BASE_URL}/repositories/{GRAPHDB_REPOSITORY_ID}. "
            f"Original error: {exc}"
        )
    return client


@pytest.mark.integration
def test_imports_two_fixture_xml_files_into_distinct_named_graphs() -> None:
    root = _project_root()
    xml_file_a, xml_file_b = _fixture_xml_files()[:2]

    base_graph_iri = f"https://example.org/graph/test-import-{uuid4().hex}"
    graph_iri_a = f"{base_graph_iri}/{xml_file_a.stem}"
    graph_iri_b = f"{base_graph_iri}/{xml_file_b.stem}"

    client = _graphdb_client()

    service = ImportXmlToCanonicalRdfService(
        graphdb_base_url=GRAPHDB_BASE_URL,
        repository_id=GRAPHDB_REPOSITORY_ID,
        element_mapping_path=str(
            root / "src" / "archimate_adapter" / "mapping" / "element_types.yaml"
        ),
        relationship_mapping_path=str(
            root
            / "src"
            / "archimate_adapter"
            / "mapping"
            / "relationship_types.yaml"
        ),
        replace_graph=False,
        graph_target_strategy="per_file",
        per_file_graph_base_iri=base_graph_iri,
    )

    try:
        imported_graph_iri_a = service.import_from_file(xml_file_a)
        imported_graph_iri_b = service.import_from_file(xml_file_b)

        assert imported_graph_iri_a == graph_iri_a
        assert imported_graph_iri_b == graph_iri_b
        assert imported_graph_iri_a != imported_graph_iri_b

        ask_a = client.ask(f"ASK {{ GRAPH <{graph_iri_a}> {{ ?s ?p ?o }} }}")
        ask_b = client.ask(f"ASK {{ GRAPH <{graph_iri_b}> {{ ?s ?p ?o }} }}")

        assert ask_a is True
        assert ask_b is True

        count_rows = client.select(
            f"""
            SELECT ?g (COUNT(*) AS ?tripleCount)
            WHERE {{
              VALUES ?g {{ <{graph_iri_a}> <{graph_iri_b}> }}
              GRAPH ?g {{ ?s ?p ?o }}
            }}
            GROUP BY ?g
            """
        )

        counts = {row["g"]: int(row["tripleCount"]) for row in count_rows}

        assert counts[graph_iri_a] > 0
        assert counts[graph_iri_b] > 0
    finally:
        # Clean up only the graphs created by this test; keep ontology/default graph intact.
        for graph_iri in (graph_iri_a, graph_iri_b):
            try:
                client.clear_graph(graph_iri)
            except GraphDBClientError:
                pass

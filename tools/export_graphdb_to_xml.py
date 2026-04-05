from pathlib import Path

from archimate_adapter.config import (
    DEFAULT_EXPORT_XML_PATH,
    DEFAULT_MODEL_GRAPH_IRI,
    ELEMENT_MAPPING_PATH,
    GRAPHDB_BASE_URL,
    GRAPHDB_REPOSITORY_ID,
    RELATIONSHIP_MAPPING_PATH,
)
from archimate_adapter.services.export_canonical_rdf_to_xml import (
    ExportCanonicalRdfToXmlService,
)


def main() -> None:
    output_path = Path(DEFAULT_EXPORT_XML_PATH)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    service = ExportCanonicalRdfToXmlService(
        graphdb_base_url=GRAPHDB_BASE_URL,
        repository_id=GRAPHDB_REPOSITORY_ID,
        element_mapping_path=str(ELEMENT_MAPPING_PATH),
        relationship_mapping_path=str(RELATIONSHIP_MAPPING_PATH),
        graph_iri=DEFAULT_MODEL_GRAPH_IRI,
    )

    service.export_to_file(str(output_path))
    print(f"Export completed: {output_path}")


if __name__ == "__main__":
    main()

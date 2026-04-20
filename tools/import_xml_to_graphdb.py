from pathlib import Path

from archimate_adapter.config import (
    DEFAULT_IMPORT_XML_PATH,
    DEFAULT_MODEL_GRAPH_IRI,
    ELEMENT_MAPPING_PATH,
    GRAPHDB_BASE_URL,
    GRAPHDB_REPOSITORY_ID,
    RELATIONSHIP_MAPPING_PATH,
)
from archimate_adapter.services.import_xml_to_canonical_rdf import (
    ImportXmlToCanonicalRdfService,
)


def main() -> None:
    input_path = Path(DEFAULT_IMPORT_XML_PATH)
    print("GRAPHDB_BASE_URL =", GRAPHDB_BASE_URL)
    print("GRAPHDB_REPOSITORY_ID =", GRAPHDB_REPOSITORY_ID)
    print("DEFAULT_MODEL_GRAPH_IRI =", DEFAULT_MODEL_GRAPH_IRI)
    print("DEFAULT_IMPORT_XML_PATH =", input_path.resolve())
    print("INPUT EXISTS =", input_path.exists())
    print("Actual path used:", str(input_path))

    service = ImportXmlToCanonicalRdfService(
        graphdb_base_url=GRAPHDB_BASE_URL,
        repository_id=GRAPHDB_REPOSITORY_ID,
        element_mapping_path=str(ELEMENT_MAPPING_PATH),
        relationship_mapping_path=str(RELATIONSHIP_MAPPING_PATH),
        graph_iri=DEFAULT_MODEL_GRAPH_IRI,
        replace_graph=True,
    )

    service.import_from_file(str(input_path))
    print(f"Import completed into graph: {DEFAULT_MODEL_GRAPH_IRI}")


if __name__ == "__main__":
    main()

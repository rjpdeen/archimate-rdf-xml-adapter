from pathlib import Path

GRAPHDB_BASE_URL = "http://localhost:7200"
GRAPHDB_REPOSITORY_ID = "archimate_phase1"
DEFAULT_MODEL_GRAPH_IRI = "https://example.org/graph/model"

ELEMENT_MAPPING_PATH = Path("src/archimate_adapter/mapping/element_types.yaml")
RELATIONSHIP_MAPPING_PATH = Path("src/archimate_adapter/mapping/relationship_types.yaml")

DEFAULT_IMPORT_XML_PATH = Path("out/VZK.xml")
DEFAULT_EXPORT_XML_PATH = Path("out/exported-from-graphdb.xml")
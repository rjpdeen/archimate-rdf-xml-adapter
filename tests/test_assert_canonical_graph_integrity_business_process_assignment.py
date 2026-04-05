from archimate_adapter.services.assert_canonical_graph_integrity import (
    AssertCanonicalGraphIntegrityService,
)


class FakeGraphDBClient:
    def __init__(self, responses: list[list[dict[str, str]]]) -> None:
        self._responses = responses
        self._call_index = 0
        self.queries: list[str] = []

    def select(self, query: str) -> list[dict[str, str]]:
        self.queries.append(query)

        if self._call_index >= len(self._responses):
            return []

        response = self._responses[self._call_index]
        self._call_index += 1
        return response


class FakeElementRegistry:
    def __init__(self) -> None:
        self.rdf_to_xml_map = {
            "https://purl.org/archimate#ApplicationComponent": {
                "xml_type": "ApplicationComponent"
            },
            "https://purl.org/archimate#BusinessActor": {
                "xml_type": "BusinessActor"
            },
            "https://purl.org/archimate#BusinessProcess": {
                "xml_type": "BusinessProcess"
            },
        }


class FakeRelationshipRegistry:
    def supported_predicate_iris(self) -> list[str]:
        return [
            "https://purl.org/archimate#serving",
            "https://purl.org/archimate#assignment",
        ]


def test_assert_graph_is_valid_accepts_assignment_between_supported_elements() -> None:
    client = FakeGraphDBClient(
        responses=[
            [],  # quoted metadata without base triple
            [],  # duplicate relationship identifier
            [],  # relationship endpoints not typed as supported elements
        ]
    )

    service = AssertCanonicalGraphIntegrityService(
        client,
        element_registry=FakeElementRegistry(),
        relationship_registry=FakeRelationshipRegistry(),
    )

    service.assert_graph_is_valid("https://example.org/graph/model")

    assert len(client.queries) == 3
    combined_queries = "\n".join(client.queries)
    assert "https://purl.org/archimate#assignment" in combined_queries
    assert "https://purl.org/archimate#BusinessProcess" in combined_queries
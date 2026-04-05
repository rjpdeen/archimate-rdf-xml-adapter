import pytest

from archimate_adapter.services.assert_canonical_graph_integrity import (
    AssertCanonicalGraphIntegrityService,
    CanonicalGraphIntegrityError,
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
        }


class FakeRelationshipRegistry:
    def supported_predicate_iris(self) -> list[str]:
        return [
            "https://purl.org/archimate#serving",
        ]


def test_assert_graph_is_valid_passes_when_no_issues() -> None:
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


def test_assert_graph_is_valid_fails_when_quoted_metadata_has_no_base_triple() -> None:
    client = FakeGraphDBClient(
        responses=[
            [
                {
                    "source": "https://example.org/app-1",
                    "predicate": "https://purl.org/archimate#serving",
                    "target": "https://example.org/actor-1",
                    "metaPredicate": "https://purl.org/archimate#identifier",
                }
            ],
            [],
            [],
        ]
    )
    service = AssertCanonicalGraphIntegrityService(
        client,
        element_registry=FakeElementRegistry(),
        relationship_registry=FakeRelationshipRegistry(),
    )

    with pytest.raises(CanonicalGraphIntegrityError) as exc_info:
        service.assert_graph_is_valid("https://example.org/graph/model")

    message = str(exc_info.value)
    assert "QUOTED_METADATA_WITHOUT_BASE_TRIPLE" in message
    assert "https://example.org/app-1" in message
    assert "https://example.org/actor-1" in message


def test_assert_graph_is_valid_fails_when_relationship_has_duplicate_identifier() -> None:
    client = FakeGraphDBClient(
        responses=[
            [],
            [
                {
                    "source": "https://example.org/app-1",
                    "predicate": "https://purl.org/archimate#serving",
                    "target": "https://example.org/actor-1",
                    "identifierCount": "2",
                }
            ],
            [],
        ]
    )
    service = AssertCanonicalGraphIntegrityService(
        client,
        element_registry=FakeElementRegistry(),
        relationship_registry=FakeRelationshipRegistry(),
    )

    with pytest.raises(CanonicalGraphIntegrityError) as exc_info:
        service.assert_graph_is_valid("https://example.org/graph/model")

    message = str(exc_info.value)
    assert "DUPLICATE_RELATIONSHIP_IDENTIFIER" in message
    assert "count=2" in message


def test_assert_graph_is_valid_fails_when_relationship_endpoint_is_not_supported_element() -> None:
    client = FakeGraphDBClient(
        responses=[
            [],
            [],
            [
                {
                    "source": "https://example.org/app-1",
                    "predicate": "https://purl.org/archimate#serving",
                    "target": "https://example.org/actor-999",
                }
            ],
        ]
    )
    service = AssertCanonicalGraphIntegrityService(
        client,
        element_registry=FakeElementRegistry(),
        relationship_registry=FakeRelationshipRegistry(),
    )

    with pytest.raises(CanonicalGraphIntegrityError) as exc_info:
        service.assert_graph_is_valid("https://example.org/graph/model")

    message = str(exc_info.value)
    assert "RELATIONSHIP_ENDPOINT_NOT_SUPPORTED_ELEMENT" in message
    assert "https://example.org/app-1" in message
    assert "https://example.org/actor-999" in message


def test_assert_graph_is_valid_reports_multiple_issues() -> None:
    client = FakeGraphDBClient(
        responses=[
            [
                {
                    "source": "https://example.org/app-1",
                    "predicate": "https://purl.org/archimate#serving",
                    "target": "https://example.org/actor-1",
                    "metaPredicate": "https://purl.org/archimate#identifier",
                }
            ],
            [
                {
                    "source": "https://example.org/app-2",
                    "predicate": "https://purl.org/archimate#serving",
                    "target": "https://example.org/actor-2",
                    "identifierCount": "2",
                }
            ],
            [
                {
                    "source": "https://example.org/app-3",
                    "predicate": "https://purl.org/archimate#serving",
                    "target": "https://example.org/actor-999",
                }
            ],
        ]
    )
    service = AssertCanonicalGraphIntegrityService(
        client,
        element_registry=FakeElementRegistry(),
        relationship_registry=FakeRelationshipRegistry(),
    )

    with pytest.raises(CanonicalGraphIntegrityError) as exc_info:
        service.assert_graph_is_valid("https://example.org/graph/model")

    err = exc_info.value
    assert len(err.issues) == 3
    assert "QUOTED_METADATA_WITHOUT_BASE_TRIPLE" in str(err)
    assert "DUPLICATE_RELATIONSHIP_IDENTIFIER" in str(err)
    assert "RELATIONSHIP_ENDPOINT_NOT_SUPPORTED_ELEMENT" in str(err)
from __future__ import annotations

from dataclasses import dataclass

from archimate_adapter.namespaces import ARCHIMATE


@dataclass(frozen=True)
class IntegrityIssue:
    code: str
    message: str


class CanonicalGraphIntegrityError(Exception):
    def __init__(self, issues: list[IntegrityIssue]) -> None:
        self.issues = issues
        joined = "\n".join(f"[{issue.code}] {issue.message}" for issue in issues)
        super().__init__(f"Canonical graph integrity check failed:\n{joined}")


class AssertCanonicalGraphIntegrityService:
    """
    Validates phase-1 canonical graph invariants for the model named graph.

    Current checks:
    1. Relationship metadata on a quoted triple must have the corresponding base triple.
    2. A quoted relationship triple must not have more than one archimate:identifier value.
    3. Relationship endpoints must exist and have a supported ArchiMate element type.
    """

    def __init__(
        self,
        graphdb_client,
        element_registry,
        relationship_registry,
    ) -> None:
        self._graphdb_client = graphdb_client
        self._element_registry = element_registry
        self._relationship_registry = relationship_registry

    def assert_graph_is_valid(self, graph_iri: str) -> None:
        issues: list[IntegrityIssue] = []
        issues.extend(self._check_quoted_metadata_has_base_triple(graph_iri))
        issues.extend(self._check_duplicate_relationship_identifier(graph_iri))
        issues.extend(
            self._check_relationship_endpoints_are_supported_elements(graph_iri)
        )

        if issues:
            raise CanonicalGraphIntegrityError(issues)

    def _check_quoted_metadata_has_base_triple(
        self,
        graph_iri: str,
    ) -> list[IntegrityIssue]:
        query = f"""
        PREFIX archimate: <{ARCHIMATE}>

        SELECT ?source ?predicate ?target ?metaPredicate
        WHERE {{
          GRAPH <{graph_iri}> {{
            << ?source ?predicate ?target >> ?metaPredicate ?metaValue .

            FILTER(
              ?metaPredicate IN (
                archimate:identifier,
                archimate:name
              )
            )

            FILTER NOT EXISTS {{
              ?source ?predicate ?target .
            }}
          }}
        }}
        """

        rows = self._graphdb_client.select(query)
        issues: list[IntegrityIssue] = []

        for row in rows:
            issues.append(
                IntegrityIssue(
                    code="QUOTED_METADATA_WITHOUT_BASE_TRIPLE",
                    message=(
                        "Quoted relationship metadata exists without base triple: "
                        f"<< {row['source']} {row['predicate']} {row['target']} >>"
                    ),
                )
            )

        return issues

    def _check_duplicate_relationship_identifier(
        self,
        graph_iri: str,
    ) -> list[IntegrityIssue]:
        query = f"""
        PREFIX archimate: <{ARCHIMATE}>

        SELECT ?source ?predicate ?target (COUNT(?identifier) AS ?identifierCount)
        WHERE {{
          GRAPH <{graph_iri}> {{
            << ?source ?predicate ?target >> archimate:identifier ?identifier .
          }}
        }}
        GROUP BY ?source ?predicate ?target
        HAVING (COUNT(?identifier) > 1)
        """

        rows = self._graphdb_client.select(query)
        issues: list[IntegrityIssue] = []

        for row in rows:
            issues.append(
                IntegrityIssue(
                    code="DUPLICATE_RELATIONSHIP_IDENTIFIER",
                    message=(
                        "Quoted relationship triple has multiple "
                        "archimate:identifier values: "
                        f"<< {row['source']} {row['predicate']} {row['target']} >> "
                        f"(count={row['identifierCount']})"
                    ),
                )
            )

        return issues

    def _check_relationship_endpoints_are_supported_elements(
        self,
        graph_iri: str,
    ) -> list[IntegrityIssue]:
        supported_relationship_predicates = (
            self._relationship_registry.supported_predicate_iris()
        )
        supported_element_type_iris = self._supported_element_type_iris()

        if not supported_relationship_predicates:
            return []

        if not supported_element_type_iris:
            return []

        relationship_predicate_values = ", ".join(
            f"<{iri}>" for iri in supported_relationship_predicates
        )
        element_type_values = ", ".join(
            f"<{iri}>" for iri in supported_element_type_iris
        )

        query = f"""
        SELECT ?source ?predicate ?target
        WHERE {{
          GRAPH <{graph_iri}> {{
            ?source ?predicate ?target .
            FILTER(?predicate IN ({relationship_predicate_values}))

            FILTER(
              NOT EXISTS {{
                ?source a ?sourceType .
                FILTER(?sourceType IN ({element_type_values}))
              }}
              ||
              NOT EXISTS {{
                ?target a ?targetType .
                FILTER(?targetType IN ({element_type_values}))
              }}
            )
          }}
        }}
        """

        rows = self._graphdb_client.select(query)
        issues: list[IntegrityIssue] = []

        for row in rows:
            issues.append(
                IntegrityIssue(
                    code="RELATIONSHIP_ENDPOINT_NOT_SUPPORTED_ELEMENT",
                    message=(
                        "Relationship endpoint missing supported ArchiMate element "
                        f"type: {row['source']} {row['predicate']} {row['target']}"
                    ),
                )
            )

        return issues

    def _supported_element_type_iris(self) -> list[str]:
        if hasattr(self._element_registry, "supported_element_type_iris"):
            return list(self._element_registry.supported_element_type_iris())

        if hasattr(self._element_registry, "rdf_to_xml_map"):
            return list(self._element_registry.rdf_to_xml_map.keys())

        raise AttributeError(
            "Element registry does not expose supported element type IRIs."
        )
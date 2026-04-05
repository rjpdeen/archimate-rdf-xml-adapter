from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import requests


class GraphDBClientError(RuntimeError):
    """Raised when a GraphDB request fails."""


@dataclass(slots=True)
class GraphDBClient:
    """
    Minimal GraphDB HTTP client for phase 1.

    Responsibilities:
    - execute SPARQL SELECT queries
    - execute SPARQL ASK queries
    - execute SPARQL UPDATE statements
    - upload RDF/Turtle-star files to a repository
    """

    base_url: str
    repository_id: str
    timeout_seconds: int = 30

    @property
    def repository_url(self) -> str:
        return f"{self.base_url.rstrip('/')}/repositories/{self.repository_id}"

    @property
    def statements_url(self) -> str:
        return f"{self.repository_url}/statements"

    def select(self, query: str) -> list[dict[str, Any]]:
        """
        Execute a SPARQL SELECT query and return rows as plain dicts.

        Output example:
        [
            {
                "element": "https://example.org/archi/model/app-1",
                "type": "https://purl.org/archimate#ApplicationComponent",
                "id": "app-1",
                "name": "My Application"
            }
        ]
        """
        response = requests.post(
            self.repository_url,
            data={"query": query},
            headers={"Accept": "application/sparql-results+json"},
            timeout=self.timeout_seconds,
        )
        self._raise_for_status(response, "SPARQL SELECT failed")

        payload = response.json()
        return self._sparql_json_bindings_to_rows(payload)

    def ask(self, query: str) -> bool:
        """
        Execute a SPARQL ASK query and return True/False.
        """
        response = requests.post(
            self.repository_url,
            data={"query": query},
            headers={"Accept": "application/sparql-results+json"},
            timeout=self.timeout_seconds,
        )
        self._raise_for_status(response, "SPARQL ASK failed")

        payload = response.json()
        value = payload.get("boolean")
        if not isinstance(value, bool):
            raise GraphDBClientError(
                f"Unexpected ASK response payload: {payload}"
            )
        return value

    def update(self, query: str) -> None:
        """
        Execute a SPARQL UPDATE statement.
        """
        response = requests.post(
            self.statements_url,
            data=query.encode("utf-8"),
            headers={"Content-Type": "application/sparql-update; charset=utf-8"},
            timeout=self.timeout_seconds,
        )
        self._raise_for_status(response, "SPARQL UPDATE failed")

    def upload_file(
        self,
        file_path: str | Path,
        content_type: str = "text/x-turtlestar",
    ) -> None:
        """
        Upload an RDF file to the repository statements endpoint.

        Default content type is Turtle-star because phase 1 uses RDF-star.
        For plain Turtle you can pass:
            content_type="text/turtle"
        """
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(path)

        with path.open("rb") as handle:
            response = requests.post(
                self.statements_url,
                data=handle,
                headers={"Content-Type": content_type},
                timeout=self.timeout_seconds,
            )

        self._raise_for_status(
            response,
            f"RDF upload failed for file: {path}",
        )

    def clear_repository(self) -> None:
        """
        Delete all statements from the repository.

        Useful for repeatable local smoke tests.
        """
        response = requests.delete(
            self.statements_url,
            timeout=self.timeout_seconds,
        )
        self._raise_for_status(response, "Failed to clear repository")

    def _sparql_json_bindings_to_rows(
        self,
        payload: dict[str, Any],
    ) -> list[dict[str, Any]]:
        results = payload.get("results", {})
        bindings = results.get("bindings", [])

        rows: list[dict[str, Any]] = []
        for binding in bindings:
            row: dict[str, Any] = {}
            for var_name, var_value in binding.items():
                row[var_name] = var_value.get("value")
            rows.append(row)

        return rows

    @staticmethod
    def _raise_for_status(response: requests.Response, message: str) -> None:
        if response.ok:
            return

        body = response.text.strip()
        if body:
            raise GraphDBClientError(
                f"{message}: HTTP {response.status_code}: {body}"
            )
        raise GraphDBClientError(f"{message}: HTTP {response.status_code}")
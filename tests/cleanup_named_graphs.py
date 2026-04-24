from __future__ import annotations

import argparse
from typing import Iterable

from archimate_adapter.config import GRAPHDB_BASE_URL, GRAPHDB_REPOSITORY_ID
from archimate_adapter.graphdb.client import GraphDBClient


def _client() -> GraphDBClient:
    return GraphDBClient(
        base_url=GRAPHDB_BASE_URL,
        repository_id=GRAPHDB_REPOSITORY_ID,
        timeout_seconds=30,
    )


def _select_graphs_by_prefix(client: GraphDBClient, prefix: str) -> list[str]:
    escaped_prefix = prefix.replace('\\', '\\\\').replace('"', '\\"')
    rows = client.select(
        f'''
        SELECT DISTINCT ?g
        WHERE {{
          GRAPH ?g {{ ?s ?p ?o }}
          FILTER(STRSTARTS(STR(?g), "{escaped_prefix}"))
        }}
        ORDER BY ?g
        '''
    )
    return [row["g"] for row in rows]


def _clear_graphs(client: GraphDBClient, graph_iris: Iterable[str]) -> None:
    for graph_iri in graph_iris:
        client.clear_graph(graph_iri)
        print(f"Cleared graph: {graph_iri}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Clear named graphs from GraphDB by exact IRI or by a common prefix."
        )
    )
    parser.add_argument(
        "--graph-iri",
        action="append",
        default=[],
        help="Exact graph IRI to clear. Can be provided multiple times.",
    )
    parser.add_argument(
        "--prefix",
        help="Clear all named graphs whose IRI starts with this prefix.",
    )
    args = parser.parse_args()

    if not args.graph_iri and not args.prefix:
        parser.error("Provide at least one --graph-iri or a --prefix.")

    client = _client()
    graph_iris: list[str] = list(args.graph_iri)

    if args.prefix:
        matched_graphs = _select_graphs_by_prefix(client, args.prefix)
        if not matched_graphs:
            print(f"No named graphs found for prefix: {args.prefix}")
        else:
            print("Matched named graphs:")
            for graph_iri in matched_graphs:
                print(graph_iri)
            graph_iris.extend(matched_graphs)

    unique_graph_iris = sorted(set(graph_iris))
    if not unique_graph_iris:
        print("Nothing to clear.")
        return

    _clear_graphs(client, unique_graph_iris)


if __name__ == "__main__":
    main()

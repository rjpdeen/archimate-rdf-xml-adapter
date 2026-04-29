import csv
import html
from pathlib import Path

INPUT_FILE = Path("out/query-result.tsvs")
OUTPUT_FILE = Path("out/yed_graph.graphml")

def short_label(value: str) -> str:
    """Maakt URI's wat leesbaarder."""
    if not value:
        return ""

    value = value.strip()

    if "#" in value:
        return value.rsplit("#", 1)[-1]

    if "/" in value:
        return value.rstrip("/").rsplit("/", 1)[-1]

    return value


def read_tsvs(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f, delimiter="\t")
        rows = []

        for row in reader:
            clean_row = {}

            for key, value in row.items():
                if key is None:
                    continue

                clean_key = key.strip().lstrip("?")
                clean_value = (value or "").strip()

                # GraphDB/SPARQL TSV gebruikt soms <...> rond URI's
                if clean_value.startswith("<") and clean_value.endswith(">"):
                    clean_value = clean_value[1:-1]

                # Literals kunnen soms quotes bevatten
                if clean_value.startswith('"') and clean_value.endswith('"'):
                    clean_value = clean_value[1:-1]

                clean_row[clean_key] = clean_value

            rows.append(clean_row)

        return rows


def add_node(nodes: dict, node_id: str, label: str, node_type: str):
    if node_id not in nodes:
        nodes[node_id] = {
            "label": label or short_label(node_id),
            "type": node_type or "",
        }

def style_for_type(node_type: str) -> dict[str, str]:
    if node_type == "ApplicationComponent":
        return {
            "fill": "#B8D7F5",
            "border": "#3B73AF",
            "shape": "roundrectangle",
        }

    if node_type == "BusinessProcess":
        return {
            "fill": "#F5D6A8",
            "border": "#B8791F",
            "shape": "rectangle",
        }
    
    if node_type == "ApplicationService":
        return {
            "fill": "#D6EAF8",
            "border": "#2874A6",
            "shape": "hexagon",
        }

    return {
        "fill": "#E0E0E0",
        "border": "#666666",
        "shape": "roundrectangle",
    }

def make_graphml(rows: list[dict[str, str]]) -> str:
    nodes = {}
    edges = []

    for row in rows:
        source = row.get("source", "").strip()
        target = row.get("target", "").strip()

        if not source:
            continue

        source_label = row.get("sourceLabel", "").strip()
        target_label = row.get("targetLabel", "").strip()
        source_type = row.get("sourceType", "").strip()
        target_type = row.get("targetType", "").strip()
        relation_label = row.get("relationLabel", "").strip()

        add_node(nodes, source, source_label, source_type)

        if target:
            add_node(nodes, target, target_label, target_type)

            edges.append({
                "source": source,
                "target": target,
                "label": relation_label or short_label(row.get("relation", "")),
            })

        edges.append({
            "source": source,
            "target": target,
            "label": relation_label or short_label(row.get("relation", "")),
        })

    lines = []

    lines.append('<?xml version="1.0" encoding="UTF-8"?>')
    lines.append('<graphml xmlns="http://graphml.graphdrawing.org/xmlns"')
    lines.append('         xmlns:y="http://www.yworks.com/xml/graphml">')

    lines.append('  <key id="d0" for="node" yfiles.type="nodegraphics"/>')
    lines.append('  <key id="d1" for="edge" yfiles.type="edgegraphics"/>')

    lines.append('  <graph id="G" edgedefault="directed">')

    for node_id, data in nodes.items():
        safe_id = html.escape(node_id, quote=True)
        safe_label = html.escape(data["label"], quote=True)
        style = style_for_type(data["type"])

        lines.append(f'    <node id="{safe_id}">')
        lines.append('      <data key="d0">')
        lines.append('        <y:ShapeNode>')
        lines.append('          <y:Geometry height="40.0" width="180.0" x="0.0" y="0.0"/>')
        lines.append(f'          <y:Fill color="{style["fill"]}" transparent="false"/>')
        lines.append(f'          <y:BorderStyle color="{style["border"]}" type="line" width="1.5"/>')
        lines.append(f'          <y:NodeLabel>{safe_label}</y:NodeLabel>')
        lines.append(f'          <y:Shape type="{style["shape"]}"/>')
        lines.append('        </y:ShapeNode>')
        lines.append('      </data>')
        lines.append('    </node>')

    for i, edge in enumerate(edges, start=1):
        safe_source = html.escape(edge["source"], quote=True)
        safe_target = html.escape(edge["target"], quote=True)
        safe_label = html.escape(edge["label"], quote=True)

        lines.append(f'    <edge id="e{i}" source="{safe_source}" target="{safe_target}">')
        lines.append('      <data key="d1">')
        lines.append('        <y:PolyLineEdge>')
        lines.append(f'          <y:EdgeLabel>{safe_label}</y:EdgeLabel>')
        lines.append('          <y:Arrows source="none" target="standard"/>')
        lines.append('        </y:PolyLineEdge>')
        lines.append('      </data>')
        lines.append('    </edge>')

    lines.append('  </graph>')
    lines.append('</graphml>')

    return "\n".join(lines)


def main():
    rows = read_tsvs(INPUT_FILE)
    graphml = make_graphml(rows)
    OUTPUT_FILE.write_text(graphml, encoding="utf-8")

    print(f"GraphML geschreven naar: {OUTPUT_FILE}")
    print(f"Aantal rijen gelezen: {len(rows)}")


if __name__ == "__main__":
    main()
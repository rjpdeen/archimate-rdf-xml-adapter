import re
from pathlib import Path

ID_PATTERN = re.compile(
    r"\b(?:"
    r"EAID_[0-9a-fA-F]{8}_[0-9a-fA-F]{4}_[0-9a-fA-F]{4}_[0-9a-fA-F]{4}_[0-9a-fA-F]{12}"
    r"|"
    r"[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}"
    r")\b"
)

def replace_ids(text: str) -> tuple[str, dict[str, str]]:
    original_to_short_id = {}
    counter = 1

    def replace_match(match: re.Match) -> str:
        nonlocal counter

        original_id = match.group(0)

        if original_id not in original_to_short_id:
            original_to_short_id[original_id] = f"ID{counter}"
            counter += 1

        return original_to_short_id[original_id]

    new_text = ID_PATTERN.sub(replace_match, text)
    return new_text, original_to_short_id


def main():
    input_file = Path("out/input.txt")
    output_file = Path("out/output.txt")
    mapping_file = Path("id_mapping.txt")

    text = input_file.read_text(encoding="utf-8")

    new_text, mapping = replace_ids(text)

    output_file.write_text(new_text, encoding="utf-8")

    mapping_lines = [
        f"{short_id} = {original_id}"
        for original_id, short_id in mapping.items()
    ]
    mapping_file.write_text("\n".join(mapping_lines), encoding="utf-8")

    print(f"Replaced text written to: {output_file}")
    print(f"Mapping written to: {mapping_file}")


if __name__ == "__main__":
    main()
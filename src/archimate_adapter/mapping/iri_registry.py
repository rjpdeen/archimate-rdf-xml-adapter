from urllib.parse import quote, unquote


BASE_MODEL_IRI = "https://example.org/archi/model/"


def element_iri(identifier: str) -> str:
    _validate_identifier(identifier)
    return f"{BASE_MODEL_IRI}{quote(identifier, safe='')}"


def identifier_from_iri(iri: str) -> str:
    if not iri.startswith(BASE_MODEL_IRI):
        raise ValueError(f"IRI outside model namespace: {iri}")
    return unquote(iri[len(BASE_MODEL_IRI):])


def is_model_iri(iri: str) -> bool:
    return iri.startswith(BASE_MODEL_IRI)


def relationship_key(source_id: str, predicate_iri: str, target_id: str) -> tuple[str, str, str]:
    _validate_identifier(source_id)
    _validate_identifier(target_id)
    if not predicate_iri:
        raise ValueError("predicate_iri must not be empty")
    return (source_id, predicate_iri, target_id)


def _validate_identifier(identifier: str) -> None:
    if not identifier:
        raise ValueError("identifier must not be empty")
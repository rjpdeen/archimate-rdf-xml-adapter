# ArchiMate RDF to XML Adapter

Phase 1 prototype for roundtrip between ArchiMate Exchange XML and canonical RDF, without views, layout, or diagram information.

## Purpose

This repository contains a prototype adapter for importing ArchiMate Exchange XML into a canonical RDF representation in GraphDB and exporting that canonical RDF back to ArchiMate Exchange XML.

The focus in **Phase 1** is on:

- roundtrip of **elements and relationships**
- using **GraphDB** as the canonical backend
- using the **Mendoza ArchiMate ontology** as the RDF vocabulary
- preserving **relationship metadata** via **RDF-star**
- **not** supporting:
  - views
  - layout / diagram information
  - bendpoints
  - style / visual properties

## Architecture choices

### Canonical backend

The canonical store is **GraphDB**.

### Canonical RDF form

The canonical RDF form uses:

- **Mendoza-native relationships as object properties**
- **no adapter-level relationship instance resource**
- **relationship metadata on the quoted triple via RDF-star**

Example:

```turtle
ex:app-1 archimate:serving ex:actor-1 .

<< ex:app-1 archimate:serving ex:actor-1 >>
  archimate:identifier "rel-1" ;
  archimate:name "serves"@en ;
  dct:description "Application serves actor in this model."@en .
```

## Graph usage in GraphDB

- default graph = ontology / base
- named graph = model instance data for import / export / roundtrip

Important:

- the ontology/base must be loaded separately
- model data lives in a named graph
- relationship metadata belongs to the quoted triple, not to the relationship property itself

## Phase 1 scope

This phase supports only the **Business** and **Application** scope of the adapter, without diagram information.

The implementation has been built incrementally and tested in batches.

## Supported element types

### Application layer

- ApplicationComponent
- ApplicationCollaboration
- ApplicationInterface
- ApplicationFunction
- ApplicationProcess
- ApplicationInteraction
- ApplicationEvent
- ApplicationService
- DataObject

### Business layer

- BusinessActor
- BusinessRole
- BusinessCollaboration
- BusinessInterface
- BusinessFunction
- BusinessProcess
- BusinessInteraction
- BusinessEvent
- BusinessService
- BusinessObject
- BusinessContract
- Product
- Representation

## Supported relationship types

The current Phase 1 prototype supports the following relationship types:

- Access
- Aggregation
- Assignment
- Association
- Composition
- Flow
- Influence
- Realization
- Serving
- Specialization
- Triggering

## What is not supported in Phase 1

Phase 1 does **not** yet support:

- Motivation, Technology, Physical, Strategy, or Implementation and Migration layers beyond the currently listed subset
- views
- node / connection layout
- styles
- bendpoints
- labels beyond element / relationship metadata
- diagram-level information
- full ArchiMate language coverage

## Important integrity rules

The `assert_canonical_graph_integrity.py` service checks, among other things:

- quoted relationship metadata must have a corresponding base triple
- a quoted relationship triple must not have more than one `archimate:identifier`
- relationship endpoints must exist and must have supported ArchiMate element types

## Repository structure

```text
src/
  archimate_adapter/
    dto/
      model.py
    graphdb/
      client.py
      export_queries.py
    mapping/
      element_types.yaml
      relationship_types.yaml
      registry.py
    services/
      assert_canonical_graph_integrity.py
      export_canonical_rdf_to_xml.py
      import_xml_to_canonical_rdf.py
      rdf_to_xml.py
      xml_to_rdf.py
    xml/
      parser.py
      writer.py

tests/
  fixtures/
    xml/
      ...
  test_*.py

docker/
  graphdb/
    docker-compose.yml
    ...

README.md
```

## Requirements

- Python 3.14.x
- Docker Desktop
- GraphDB
- pytest

## Starting GraphDB

Go to the GraphDB Docker folder and start the container:

```powershell
cd docker/graphdb
docker compose up -d
```

View logs:

```powershell
docker compose logs -f graphdb
```

The GraphDB Workbench is normally available at:

```text
http://localhost:7200
```

## GraphDB repository

The tests assume a GraphDB repository with id:

```text
archimate_phase1
```

Make sure this repository exists before running the integration tests.

## Loading the ontology/base

The default graph must contain the ontology/base. The model data must live in a named graph.

Use your existing GraphDB setup and loading steps for:

- the Mendoza ontology


## How to use this repository

A typical usage flow is:

1. start GraphDB
2. make sure the repository `archimate_phase1` exists
3. load the Mendoza ontology and minimal base data into the **default graph**
4. choose a **named graph** for your model instance data
5. import an ArchiMate Exchange XML file into canonical RDF
6. inspect or validate the canonical RDF in GraphDB
7. export the canonical RDF back to ArchiMate Exchange XML
8. run the automated tests to verify the roundtrip behavior

## Quick start

### 1. Start GraphDB

```powershell
cd docker/graphdb
docker compose up -d
```

### 2. Prepare GraphDB

Make sure:

- GraphDB is reachable
- repository `archimate_phase1` exists
- the Mendoza ontology is loaded in the default graph

### 3. Import XML into canonical RDF

```python
from archimate_adapter.services.import_xml_to_canonical_rdf import (
    ImportXmlToCanonicalRdfService,
)

service = ImportXmlToCanonicalRdfService(
    graphdb_base_url="http://localhost:7200",
    repository_id="archimate_phase1",
    element_mapping_path="src/archimate_adapter/mapping/element_types.yaml",
    relationship_mapping_path="src/archimate_adapter/mapping/relationship_types.yaml",
    graph_iri="https://example.org/graph/model",
)

service.import_from_file("tests/fixtures/xml/phase1_supported_types.xml")
```

What this does:

- parses the ArchiMate Exchange XML file
- maps XML element and relationship types using the YAML mapping files
- writes canonical RDF into the selected named graph in GraphDB
- stores relationship metadata using RDF-star on quoted triples

### 4. Export canonical RDF back to XML

```python
from archimate_adapter.services.export_canonical_rdf_to_xml import (
    ExportCanonicalRdfToXmlService,
)

service = ExportCanonicalRdfToXmlService(
    graphdb_base_url="http://localhost:7200",
    repository_id="archimate_phase1",
    element_mapping_path="src/archimate_adapter/mapping/element_types.yaml",
    relationship_mapping_path="src/archimate_adapter/mapping/relationship_types.yaml",
    graph_iri="https://example.org/graph/model",
)

service.export_to_file("out.xml")
```

What this does:

- reads canonical RDF for the selected named graph
- translates RDF classes and predicates back to ArchiMate Exchange XML types
- writes an Exchange XML file for roundtrip verification

## How the adapter works

### XML to RDF

- the parser reads ArchiMate Exchange XML
- XML types are translated via YAML mappings to Mendoza RDF classes and predicates
- the model is inserted as canonical triples into GraphDB
- relationship metadata is stored via RDF-star on the quoted triple

### RDF to XML

- an export query reads element and relationship data from the named graph
- the mapping determines the translation back to Exchange XML `xsi:type`
- the writer outputs an ArchiMate Exchange XML file

## Important design principle

This adapter does not use a canonical relationship resource as an intermediate layer.

So not:

- a separate RDF resource for each relationship instance

But instead:

- the base triple as the canonical relationship
- metadata on the quoted triple via RDF-star

This keeps the canonical form close to the Mendoza ontology.

## Important implementation lesson

In GraphDB visualization, multiple predicates may appear on one edge, for example a concrete relationship plus an inferred super-property such as `structuralRelationship`.

This is expected behavior and not a roundtrip bug.

## Running tests

### Run one batch test

Example:

```powershell
py -m pytest tests/test_business_completion_batch.py -v
```

### Run integration tests only

```powershell
py -m pytest -m integration -v
```

### Run the mixed roundtrip test

```powershell
py -m pytest tests/test_roundtrip_supported_phase1_types.py -v
```

### Run everything

```powershell
py -m pytest -v
```

## What the tests cover

The test strategy is built from:

- parser tests
- SPARQL build tests
- import integration tests
- export integration tests
- mixed roundtrip test for the full supported subset

Each batch usually has one combined test file.

## Practical workflow

The usual workflow is:

1. start GraphDB
2. make sure repository `archimate_phase1` exists
3. load ontology/base into the default graph
4. import a supported Exchange XML model into a named graph
5. run batch tests
6. run the mixed roundtrip test
7. export the model back to XML
8. optionally inspect the exported XML manually in Archi or another tool

## Git workflow

To commit and push to GitHub:

```powershell
git status
git add .
git commit -m "Complete phase 1 business and application layer support"
git push
```

## Status

The Phase 1 prototype adapter now supports a broad Business and Application subset with roundtrip through GraphDB and RDF-star relationship metadata.

The next logical step after Phase 1 is extension toward:

- additional ArchiMate layers
- views / diagram information
- broader language coverage
- stronger validation

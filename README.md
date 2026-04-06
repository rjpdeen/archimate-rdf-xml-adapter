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

## Quick start with GraphDB and tools

### 0. Grapdb licence

This repository does **not** include a GraphDB license file.

Starting with GraphDB 11, GraphDB Free requires a license file that you must request yourself. You can request a free GraphDB license on the Ontotext GraphDB download page. Ontotext will send the free license to your email address. 

After receiving your license file, place it here, with this exact name:

```text
docker/graphdb/init/GRAPHDB_FREE_v11.3.license
```

The Docker setup expects the license file at that path.

### 1. Start GraphDB

If you only want to start GraphDB locally, Docker is sufficient:

```powershell
cd docker/graphdb
docker compose up -d
```

View logs (it may take a minute to set up GraphDB):

```powershell
docker compose logs -f graphdb
```

The GraphDB Workbench is normally available at:

```text
http://localhost:7200
```

When you open GraphDB portal, you should see a repo and a loaded base model (default graph).

### 2. Import XML into canonical RDF

```powershell
py tools/import_xml_to_graphdb.py
```

This transforms the selected XML file into canonical RDF in GraphDB in a separate named model graph.

### 3. Export canonical RDF back to XML
You can make some changes in the imported model, before exporting it back to XML format.

```powershell
py tools/export_graphdb_to_xml.py
```

By default, the tools use settings from:

```text
src/archimate_adapter/config.py
```


## GraphDB repository and base model

The tools and integration tests assume a GraphDB repository with id:

```text
archimate_phase1
```

This repository is created automatically by the Docker GraphDB init flow.

No manual action is needed after cloning for the ontology/base initialization.

When you start GraphDB with:

```powershell
cd docker/graphdb
docker compose up -d
```

the init flow automatically creates the repository and loads `archimate.ttl` into the default graph as the base model.

That base model is not deleted when you import an XML file. XML import writes the imported model to a separate named graph.

## Choose the XML file to import

The first manual action after cloning is choosing the ArchiMate Exchange XML file you want to import into GraphDB.

By default, the import tool expects this file:

```text
out/phase1_supported_types.xml
```

So after cloning the repo, you can either:

- use that default file which is present in `out/`
- or place another XML file in `out/` and update the path in `src/archimate_adapter/config.py`


## Canonical RDF form

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

The GraphDB setup uses two distinct kinds of data:

- **default graph** = ontology / base model
- **named graph** = imported model instance data

Important:

- `archimate.ttl` is loaded automatically as the base model in GraphDB
- that base model remains present when you import an XML file
- importing an XML file creates or updates a **separate model graph** in GraphDB
- relationship metadata belongs to the quoted triple, not to the relationship property itself

## Phase 1 scope

This phase supports only the **Business** and **Application** scope of the adapter, without diagram information.

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
- Contract
- Product
- Representation

Note: this project uses `Contract` consistently to align with the ArchiMate Exchange format. This is a deliberate deviation from upstream Mendoza naming on this point.

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
archimate-rdf-xml-adapter/
├─ src/
│  └─ archimate_adapter/
│     ├─ dto/
│     │  └─ model.py
│     ├─ graphdb/
│     │  ├─ client.py
│     │  └─ export_queries.py
│     ├─ mapping/
│     │  ├─ element_types.yaml
│     │  ├─ relationship_types.yaml
│     │  ├─ iri_registry.py
│     │  └─ registry.py
│     ├─ services/
│     │  ├─ assert_canonical_graph_integrity.py
│     │  ├─ export_canonical_rdf_to_xml.py
│     │  ├─ import_xml_to_canonical_rdf.py
│     │  ├─ rdf_to_xml.py
│     │  └─ xml_to_rdf.py
│     ├─ xml/
│     │  ├─ parser.py
│     │  └─ writer.py
│     ├─ config.py
│     └─ namespaces.py
├─ tests/
│  ├─ fixtures/
│  │  └─ xml/
│  └─ test_*.py
├─ examples/
│  └─ xml/
├─ tools/
│  ├─ export_graphdb_to_xml.py
│  └─ import_xml_to_graphdb.py
├─ docker/
│  └─ graphdb/
│     ├─ docker-compose.yml
│     └─ init/
│        ├─ archimate.ttl
│        ├─ init-graphdb.sh
│        ├─ minimal-mendoza-base.ttl
│        ├─ minimal-phase1-model.ttls
│        └─ repo-config.ttl
├─ ontology/
├─ out/
├─ .gitignore
├─ .gitattributes
├─ pyproject.toml
└─ README.md
```

## Working directories

- `tests/fixtures/xml/`: XML fixtures used by automated tests
- `examples/xml/`: example XML files committed to the repository
- `out/`: local working XML files used during manual import/export runs
- `docker/graphdb/home/`: GraphDB runtime state created locally; this should not be committed

## Requirements

- Python 3.14.x
- Docker (Desktop)
- GraphDB
- pytest


## How the adapter works

### XML to RDF

- the parser reads ArchiMate Exchange XML
- XML types are translated via YAML mappings to Mendoza RDF classes and predicates
- the model is inserted as canonical triples into a named graph in GraphDB
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


## Status

The Phase 1 prototype adapter now supports a broad Business and Application subset with roundtrip through GraphDB and RDF-star relationship metadata.

The next logical step after Phase 1 is extension toward:

- additional ArchiMate layers
- views / diagram information
- broader language coverage
- stronger validation

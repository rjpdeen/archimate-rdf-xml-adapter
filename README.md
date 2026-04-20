# ArchiMate RDF to XML Adapter

Phase 1 prototype for roundtrip between ArchiMate Exchange XML and canonical RDF, without views, viewpoints, layout, or diagram information.

## Purpose

This repository contains a prototype adapter for importing ArchiMate Exchange XML into a canonical RDF representation in GraphDB and exporting that canonical RDF back to ArchiMate Exchange XML.

The focus in **Phase 1** is on:

- roundtrip of **all ArchiMate element and relationship types in the language metamodel**
- using **GraphDB** as the canonical backend
- using the **Mendoza ArchiMate ontology** as the RDF vocabulary
- preserving **relationship metadata** via **RDF-star**
- **not** supporting:
  - views
  - viewpoints
  - layout / diagram information
  - bendpoints
  - style / visual properties

## Quick start with GraphDB and tools

Use this quick start if you want to:

- start GraphDB locally
- run the Python import/export tools
- work from your own cloned copy of this repository

### 1. Start GraphDB

This repository does **not** include a GraphDB license file.

Starting with GraphDB 11, GraphDB Free requires a license file that you must request yourself. After receiving the license file, place it here:

```text
docker/graphdb/init/GRAPHDB_FREE_v11.3.license
```

Then start GraphDB:

```powershell
cd docker/graphdb
docker compose up -d
```

You should see a repository and loaded base model in GraphDB after a while.

View logs if needed:

```powershell
docker compose logs -f graphdb
```

The GraphDB Workbench is normally available at:

```text
http://localhost:7200
```

### 2. Create a local Python environment

If you want to run the Python tools, it is recommended to create a local virtual environment in the repository root. This keeps the dependencies of this clone isolated from other Python projects on your machine.

In Windows PowerShell:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e .
```

Explanation:

- `py -m venv .venv` creates a local Python environment in the `.venv` folder
- `.\.venv\Scripts\Activate.ps1` activates that environment in PowerShell
- `pip install -e .` installs this repository in editable mode, so the tools use the local source code from this clone

If PowerShell blocks the activation script, you can allow it for the current session only:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

Then run again:

```powershell
.\.venv\Scripts\Activate.ps1
pip install -e .
```

When you open a new terminal later, activate the environment again before running the tools:

```powershell
.\.venv\Scripts\Activate.ps1
```

### 3. GraphDB repository and ontology/base

The tools and integration tests assume a GraphDB repository with id:

```text
archimate_phase1
```

This repository is created automatically by the Docker GraphDB init flow.

No manual action is needed for the ontology/base initialization. When GraphDB starts, the init flow creates the repository and loads `archimate.ttl` into the default graph as the base model.

That base model remains present when you import an XML file. XML import writes the imported model into a separate named graph.

### 4. Choose the XML file to import

Place the XML file you want to import in `out/`, for example:

```text
out/phase1_supported_types.xml
```

If you want to use a different file, update the default import path in:

```text
src/archimate_adapter/config.py
```

### 5. Import XML into canonical RDF

Run:

```powershell
py tools/import_xml_to_graphdb.py
```

This transforms the selected XML file into canonical RDF in GraphDB in a separate named model graph.

### 6. Export canonical RDF back to XML

Run:

```powershell
py tools/export_graphdb_to_xml.py
```

By default, the tools use the settings from:

```text
src/archimate_adapter/config.py
```

## Run tests if needed

Example:

```powershell
py -m pytest tests/test_business_completion_batch.py -v
```

Run integration tests only:

```powershell
py -m pytest -m integration -v
```

Run everything:

```powershell
py -m pytest -v
```

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

This phase supports the full ArchiMate language metamodel for **elements** and **relationships**, with the explicit exception of:

- views
- viewpoints
- layout / diagram information

That means the adapter now covers all layers and the generic language concepts at the model level:

- Strategy
- Business
- Application
- Technology
- Physical
- Motivation
- Implementation & Migration
- Other generic concepts such as Grouping, Location, and Junction

## Supported element types

The current mappings cover all ArchiMate element types in the language metamodel, excluding view/viewpoint constructs.

### Strategy layer

- Capability
- CourseOfAction
- Resource
- ValueStream

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
- Representation
- Product

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

### Technology layer

- Node
- Device
- SystemSoftware
- TechnologyCollaboration
- TechnologyInterface
- TechnologyFunction
- TechnologyProcess
- TechnologyInteraction
- TechnologyEvent
- TechnologyService
- Path
- CommunicationNetwork

### Physical layer

- Equipment
- Facility
- DistributionNetwork
- Material

### Motivation layer

- Stakeholder
- Driver
- Assessment
- Goal
- Outcome
- Principle
- Requirement
- Constraint
- Meaning
- Value

### Implementation & Migration layer

- WorkPackage
- Deliverable
- ImplementationEvent
- Plateau
- Gap

### Other / generic concepts

- Grouping
- Location
- AndJunction
- OrJunction

Note: this project uses `Contract` consistently to align with the ArchiMate Exchange format. This is a deliberate deviation from upstream Mendoza naming on this point.

## Supported relationship types

The current mappings cover all ArchiMate relationship types:

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

- views
- viewpoints
- node / connection layout
- styles
- bendpoints
- diagram-level information
- view-specific labels or presentation metadata

## Important integrity rules

The `assert_canonical_graph_integrity.py` service checks, among other things:

- quoted relationship metadata must have a corresponding base triple
- a quoted relationship triple must not have more than one `archimate:identifier`
- relationship endpoints must exist and must have supported ArchiMate element types
- junctions must remain semantically distinguishable as AND vs OR in the canonical form / export flow

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

The Phase 1 prototype adapter now supports the full ArchiMate language metamodel for elements and relationships, with roundtrip through GraphDB and RDF-star relationship metadata.

The main remaining gap relative to full ArchiMate Exchange support is not the language metamodel itself, but the presentation side of the exchange format:

- views
- viewpoints
- diagram/layout information
- styling and other visual metadata

from pathlib import Path

import pytest

from archimate_adapter.graphdb.client import GraphDBClient, GraphDBClientError
from archimate_adapter.namespaces import ARCHIMATE_NS, EX_NS, RDF_NS
from archimate_adapter.services.export_canonical_rdf_to_xml import (
    ExportCanonicalRdfToXmlService,
)
from archimate_adapter.services.import_xml_to_canonical_rdf import (
    ImportXmlToCanonicalRdfService,
)


@pytest.mark.integration
def test_roundtrip_supported_phase1_types(tmp_path: Path) -> None:
    source_graph_iri = "https://example.org/graph/test-roundtrip-phase1-source"
    roundtrip_graph_iri = "https://example.org/graph/test-roundtrip-phase1-roundtrip"
    exported_xml_path = tmp_path / "phase1-supported-types-roundtrip.xml"

    client = GraphDBClient(
        base_url="http://localhost:7200",
        repository_id="archimate_phase1",
    )

    source_import_service = ImportXmlToCanonicalRdfService(
        graphdb_base_url="http://localhost:7200",
        repository_id="archimate_phase1",
        element_mapping_path="src/archimate_adapter/mapping/element_types.yaml",
        relationship_mapping_path="src/archimate_adapter/mapping/relationship_types.yaml",
        graph_iri=source_graph_iri,
    )

    export_service = ExportCanonicalRdfToXmlService(
        graphdb_base_url="http://localhost:7200",
        repository_id="archimate_phase1",
        element_mapping_path="src/archimate_adapter/mapping/element_types.yaml",
        relationship_mapping_path="src/archimate_adapter/mapping/relationship_types.yaml",
        graph_iri=source_graph_iri,
    )

    roundtrip_import_service = ImportXmlToCanonicalRdfService(
        graphdb_base_url="http://localhost:7200",
        repository_id="archimate_phase1",
        element_mapping_path="src/archimate_adapter/mapping/element_types.yaml",
        relationship_mapping_path="src/archimate_adapter/mapping/relationship_types.yaml",
        graph_iri=roundtrip_graph_iri,
    )

    app_iri = f"{EX_NS}app-1"
    actor_iri = f"{EX_NS}actor-1"
    process_iri = f"{EX_NS}process-1"
    appsvc_iri = f"{EX_NS}appsvc-1"
    data_iri = f"{EX_NS}data-1"
    appfn_iri = f"{EX_NS}appfn-1"
    appi_iri = f"{EX_NS}appi-1"

    role_iri = f"{EX_NS}role-1"
    busfn_iri = f"{EX_NS}busfn-1"
    bussvc_iri = f"{EX_NS}bussvc-1"

    appcomp1_iri = f"{EX_NS}appcomp-1"
    appproc_iri = f"{EX_NS}appproc-1"
    appevt1_iri = f"{EX_NS}appevt-1"
    dataobj1_iri = f"{EX_NS}dataobj-1"
    busobj1_iri = f"{EX_NS}busobj-1"
    busproc1_iri = f"{EX_NS}busproc-1"

    appcomp2_iri = f"{EX_NS}appcomp-2"
    appcomp3_iri = f"{EX_NS}appcomp-3"
    appcollab_iri = f"{EX_NS}appcollab-1"
    appint_iri = f"{EX_NS}appint-1"
    appevt2_iri = f"{EX_NS}appevt-2"
    appsvc2_iri = f"{EX_NS}appsvc-2"
    dataobj2_iri = f"{EX_NS}dataobj-2"

    buscollab_iri = f"{EX_NS}buscollab-1"
    role2_iri = f"{EX_NS}role-2"
    actor2_iri = f"{EX_NS}actor-2"
    busint_iri = f"{EX_NS}busint-1"
    busevt_iri = f"{EX_NS}busevt-1"
    bussvc2_iri = f"{EX_NS}bussvc-2"
    busobj2_iri = f"{EX_NS}busobj-2"

    role3_iri = f"{EX_NS}role-3"
    role4_iri = f"{EX_NS}role-4"
    busif_iri = f"{EX_NS}busif-1"
    bussvc3_iri = f"{EX_NS}bussvc-3"
    contract1_iri = f"{EX_NS}contract-1"
    product1_iri = f"{EX_NS}product-1"
    representation1_iri = f"{EX_NS}representation-1"
    busobj3_iri = f"{EX_NS}busobj-3"
    busproc2_iri = f"{EX_NS}busproc-2"
    busproc3_iri = f"{EX_NS}busproc-3"

    try:
        client.update(f"CLEAR GRAPH <{source_graph_iri}>")
        client.update(f"CLEAR GRAPH <{roundtrip_graph_iri}>")

        source_import_service.import_from_file(
            "tests/fixtures/xml/phase1_supported_types.xml"
        )

        export_service.export_to_file(str(exported_xml_path))

        assert exported_xml_path.exists()

        exported_xml = exported_xml_path.read_text(encoding="utf-8")

        # All currently supported element types
        for xml_type in [
            "ApplicationCollaboration",
            "ApplicationComponent",
            "ApplicationEvent",
            "ApplicationFunction",
            "ApplicationInteraction",
            "ApplicationInterface",
            "ApplicationProcess",
            "ApplicationService",
            "BusinessActor",
            "BusinessCollaboration",
            "BusinessContract",
            "BusinessEvent",
            "BusinessFunction",
            "BusinessInteraction",
            "BusinessInterface",
            "BusinessObject",
            "BusinessProcess",
            "BusinessRole",
            "BusinessService",
            "DataObject",
            "Product",
            "Representation",
        ]:
            assert f'xsi:type="{xml_type}"' in exported_xml

        # All currently supported relationship types
        for rel_type in [
            "Serving",
            "Assignment",
            "Realization",
            "Access",
            "Composition",
            "Triggering",
            "Aggregation",
            "Association",
            "Flow",
            "Influence",
            "Specialization",
        ]:
            assert f'xsi:type="{rel_type}"' in exported_xml

        # Representative identifiers from all batches
        for identifier in [
            "app-1",
            "actor-1",
            "process-1",
            "appsvc-1",
            "data-1",
            "appfn-1",
            "appi-1",
            "role-1",
            "busfn-1",
            "bussvc-1",
            "appcomp-1",
            "appproc-1",
            "appevt-1",
            "dataobj-1",
            "busobj-1",
            "busproc-1",
            "appcomp-2",
            "appcomp-3",
            "appcollab-1",
            "appint-1",
            "appevt-2",
            "appsvc-2",
            "dataobj-2",
            "buscollab-1",
            "role-2",
            "actor-2",
            "busint-1",
            "busevt-1",
            "bussvc-2",
            "busobj-2",
            "role-3",
            "role-4",
            "busif-1",
            "bussvc-3",
            "contract-1",
            "product-1",
            "representation-1",
            "busobj-3",
            "busproc-2",
            "busproc-3",
        ]:
            assert f'identifier="{identifier}"' in exported_xml

        for rel_id in [
            "rel-1",
            "rel-2",
            "rel-3",
            "rel-4",
            "rel-5",
            "rel-6",
            "rel-8",
            "rel-9",
            "rel-10",
            "rel-11",
            "rel-12",
            "rel-13",
            "rel-14",
            "rel-15",
            "rel-16",
            "rel-17",
            "rel-18",
            "rel-19",
            "rel-20",
            "rel-21",
            "rel-22",
            "rel-23",
            "rel-24",
            "rel-25",
            "rel-26",
            "rel-27",
            "rel-28",
            "rel-29",
            "rel-30",
            "rel-31",
            "rel-32",
            "rel-33",
            "rel-34",
            "rel-35",
            "rel-36",
            "rel-37",
        ]:
            assert f'identifier="{rel_id}"' in exported_xml

        roundtrip_import_service.import_from_file(str(exported_xml_path))

        result = client.ask(
            f"""
            PREFIX rdf: <{RDF_NS}>
            PREFIX archimate: <{ARCHIMATE_NS}>

            ASK {{
              GRAPH <{roundtrip_graph_iri}> {{
                <{app_iri}> rdf:type archimate:ApplicationComponent .
                <{actor_iri}> rdf:type archimate:BusinessActor .
                <{process_iri}> rdf:type archimate:BusinessProcess .
                <{appsvc_iri}> rdf:type archimate:ApplicationService .
                <{data_iri}> rdf:type archimate:DataObject .
                <{appfn_iri}> rdf:type archimate:ApplicationFunction .
                <{appi_iri}> rdf:type archimate:ApplicationInterface .

                <{role_iri}> rdf:type archimate:BusinessRole .
                <{busfn_iri}> rdf:type archimate:BusinessFunction .
                <{bussvc_iri}> rdf:type archimate:BusinessService .

                <{appcomp1_iri}> rdf:type archimate:ApplicationComponent .
                <{appproc_iri}> rdf:type archimate:ApplicationProcess .
                <{appevt1_iri}> rdf:type archimate:ApplicationEvent .
                <{dataobj1_iri}> rdf:type archimate:DataObject .
                <{busobj1_iri}> rdf:type archimate:BusinessObject .
                <{busproc1_iri}> rdf:type archimate:BusinessProcess .

                <{appcomp2_iri}> rdf:type archimate:ApplicationComponent .
                <{appcomp3_iri}> rdf:type archimate:ApplicationComponent .
                <{appcollab_iri}> rdf:type archimate:ApplicationCollaboration .
                <{appint_iri}> rdf:type archimate:ApplicationInteraction .
                <{appevt2_iri}> rdf:type archimate:ApplicationEvent .
                <{appsvc2_iri}> rdf:type archimate:ApplicationService .
                <{dataobj2_iri}> rdf:type archimate:DataObject .

                <{buscollab_iri}> rdf:type archimate:BusinessCollaboration .
                <{role2_iri}> rdf:type archimate:BusinessRole .
                <{actor2_iri}> rdf:type archimate:BusinessActor .
                <{busint_iri}> rdf:type archimate:BusinessInteraction .
                <{busevt_iri}> rdf:type archimate:BusinessEvent .
                <{bussvc2_iri}> rdf:type archimate:BusinessService .
                <{busobj2_iri}> rdf:type archimate:BusinessObject .

                <{role3_iri}> rdf:type archimate:BusinessRole .
                <{role4_iri}> rdf:type archimate:BusinessRole .
                <{busif_iri}> rdf:type archimate:BusinessInterface .
                <{bussvc3_iri}> rdf:type archimate:BusinessService .
                <{contract1_iri}> rdf:type archimate:BusinessContract .
                <{product1_iri}> rdf:type archimate:Product .
                <{representation1_iri}> rdf:type archimate:Representation .
                <{busobj3_iri}> rdf:type archimate:BusinessObject .
                <{busproc2_iri}> rdf:type archimate:BusinessProcess .
                <{busproc3_iri}> rdf:type archimate:BusinessProcess .

                <{app_iri}> archimate:serving <{actor_iri}> .
                <{actor_iri}> archimate:assignment <{process_iri}> .
                <{app_iri}> archimate:realization <{appsvc_iri}> .
                <{app_iri}> archimate:access <{data_iri}> .
                <{appfn_iri}> archimate:realization <{appsvc_iri}> .
                <{app_iri}> archimate:composition <{appi_iri}> .

                <{busfn_iri}> archimate:realization <{bussvc_iri}> .
                <{role_iri}> archimate:assignment <{busfn_iri}> .

                <{appcomp1_iri}> archimate:assignment <{appproc_iri}> .
                <{appproc_iri}> archimate:realization <{appsvc_iri}> .
                <{appevt1_iri}> archimate:triggering <{appproc_iri}> .
                <{appproc_iri}> archimate:access <{dataobj1_iri}> .
                <{dataobj1_iri}> archimate:realization <{busobj1_iri}> .
                <{appsvc_iri}> archimate:serving <{busproc1_iri}> .

                <{appcollab_iri}> archimate:aggregation <{appcomp2_iri}> .
                <{appcollab_iri}> archimate:aggregation <{appcomp3_iri}> .
                <{appcollab_iri}> archimate:assignment <{appint_iri}> .
                <{appint_iri}> archimate:realization <{appsvc2_iri}> .
                <{appint_iri}> archimate:access <{dataobj2_iri}> .
                <{appevt2_iri}> archimate:triggering <{appint_iri}> .

                <{buscollab_iri}> archimate:aggregation <{role2_iri}> .
                <{buscollab_iri}> archimate:aggregation <{actor2_iri}> .
                <{buscollab_iri}> archimate:assignment <{busint_iri}> .
                <{busint_iri}> archimate:realization <{bussvc2_iri}> .
                <{busint_iri}> archimate:access <{busobj2_iri}> .
                <{busevt_iri}> archimate:triggering <{busint_iri}> .

                <{role3_iri}> archimate:composition <{busif_iri}> .
                <{busif_iri}> archimate:serving <{bussvc3_iri}> .
                <{bussvc3_iri}> archimate:association <{contract1_iri}> .
                <{product1_iri}> archimate:aggregation <{bussvc3_iri}> .
                <{product1_iri}> archimate:aggregation <{contract1_iri}> .
                <{representation1_iri}> archimate:realization <{busobj3_iri}> .
                <{busproc2_iri}> archimate:access <{representation1_iri}> .
                <{busproc2_iri}> archimate:flow <{busproc3_iri}> .
                <{busproc2_iri}> archimate:influence <{busproc3_iri}> .
                <{role3_iri}> archimate:specialization <{role4_iri}> .

                << <{app_iri}> archimate:serving <{actor_iri}> >>
                  archimate:identifier "rel-1" .
                << <{actor_iri}> archimate:assignment <{process_iri}> >>
                  archimate:identifier "rel-2" .
                << <{app_iri}> archimate:realization <{appsvc_iri}> >>
                  archimate:identifier "rel-3" .
                << <{app_iri}> archimate:access <{data_iri}> >>
                  archimate:identifier "rel-4" .
                << <{appfn_iri}> archimate:realization <{appsvc_iri}> >>
                  archimate:identifier "rel-5" .
                << <{app_iri}> archimate:composition <{appi_iri}> >>
                  archimate:identifier "rel-6" .

                << <{busfn_iri}> archimate:realization <{bussvc_iri}> >>
                  archimate:identifier "rel-8" .
                << <{role_iri}> archimate:assignment <{busfn_iri}> >>
                  archimate:identifier "rel-9" .

                << <{appcomp1_iri}> archimate:assignment <{appproc_iri}> >>
                  archimate:identifier "rel-10" .
                << <{appproc_iri}> archimate:realization <{appsvc_iri}> >>
                  archimate:identifier "rel-11" .
                << <{appevt1_iri}> archimate:triggering <{appproc_iri}> >>
                  archimate:identifier "rel-12" .
                << <{appproc_iri}> archimate:access <{dataobj1_iri}> >>
                  archimate:identifier "rel-13" .
                << <{dataobj1_iri}> archimate:realization <{busobj1_iri}> >>
                  archimate:identifier "rel-14" .
                << <{appsvc_iri}> archimate:serving <{busproc1_iri}> >>
                  archimate:identifier "rel-15" .

                << <{appcollab_iri}> archimate:aggregation <{appcomp2_iri}> >>
                  archimate:identifier "rel-16" .
                << <{appcollab_iri}> archimate:aggregation <{appcomp3_iri}> >>
                  archimate:identifier "rel-17" .
                << <{appcollab_iri}> archimate:assignment <{appint_iri}> >>
                  archimate:identifier "rel-18" .
                << <{appint_iri}> archimate:realization <{appsvc2_iri}> >>
                  archimate:identifier "rel-19" .
                << <{appint_iri}> archimate:access <{dataobj2_iri}> >>
                  archimate:identifier "rel-20" .
                << <{appevt2_iri}> archimate:triggering <{appint_iri}> >>
                  archimate:identifier "rel-21" .

                << <{buscollab_iri}> archimate:aggregation <{role2_iri}> >>
                  archimate:identifier "rel-22" .
                << <{buscollab_iri}> archimate:aggregation <{actor2_iri}> >>
                  archimate:identifier "rel-23" .
                << <{buscollab_iri}> archimate:assignment <{busint_iri}> >>
                  archimate:identifier "rel-24" .
                << <{busint_iri}> archimate:realization <{bussvc2_iri}> >>
                  archimate:identifier "rel-25" .
                << <{busint_iri}> archimate:access <{busobj2_iri}> >>
                  archimate:identifier "rel-26" .
                << <{busevt_iri}> archimate:triggering <{busint_iri}> >>
                  archimate:identifier "rel-27" .

                << <{role3_iri}> archimate:composition <{busif_iri}> >>
                  archimate:identifier "rel-28" .
                << <{busif_iri}> archimate:serving <{bussvc3_iri}> >>
                  archimate:identifier "rel-29" .
                << <{bussvc3_iri}> archimate:association <{contract1_iri}> >>
                  archimate:identifier "rel-30" .
                << <{product1_iri}> archimate:aggregation <{bussvc3_iri}> >>
                  archimate:identifier "rel-31" .
                << <{product1_iri}> archimate:aggregation <{contract1_iri}> >>
                  archimate:identifier "rel-32" .
                << <{representation1_iri}> archimate:realization <{busobj3_iri}> >>
                  archimate:identifier "rel-33" .
                << <{busproc2_iri}> archimate:access <{representation1_iri}> >>
                  archimate:identifier "rel-34" .
                << <{busproc2_iri}> archimate:flow <{busproc3_iri}> >>
                  archimate:identifier "rel-35" .
                << <{busproc2_iri}> archimate:influence <{busproc3_iri}> >>
                  archimate:identifier "rel-36" .
                << <{role3_iri}> archimate:specialization <{role4_iri}> >>
                  archimate:identifier "rel-37" .
              }}
            }}
            """
        )

        assert result is True

    finally:
        try:
            client.update(f"CLEAR GRAPH <{source_graph_iri}>")
        except GraphDBClientError:
            pass

        try:
            client.update(f"CLEAR GRAPH <{roundtrip_graph_iri}>")
        except GraphDBClientError:
            pass
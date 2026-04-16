from pathlib import Path

import pytest

from archimate_adapter.xml.parser import (
    ArchimateXmlParseError,
    parse_archimate_model,
    parse_archimate_model_string,
)


def test_parse_minimal_model():
    xml_text = """\
    <model xmlns="http://www.opengroup.org/xsd/archimate/3.0/"
           xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
           identifier="model-1"
           version="1.0">
      <name xml:lang="en">Demo model</name>
      <elements>
        <element identifier="app-1" xsi:type="ApplicationComponent">
          <name xml:lang="en">My App</name>
        </element>
        <element identifier="actor-1" xsi:type="BusinessActor">
          <name xml:lang="en">Customer</name>
        </element>
      </elements>
      <relationships>
        <relationship identifier="rel-1"
                      xsi:type="Serving"
                      source="app-1"
                      target="actor-1">
          <name xml:lang="en">serves</name>
          <documentation xml:lang="en">Application serves actor in this model.</documentation>
        </relationship>
      </relationships>
    </model>
    """

    model = parse_archimate_model_string(xml_text)

    assert len(model.elements) == 2
    assert len(model.relationships) == 1

    app = model.get_element("app-1")
    assert app.xml_type == "ApplicationComponent"
    assert app.name == "My App"

    actor = model.get_element("actor-1")
    assert actor.xml_type == "BusinessActor"
    assert actor.name == "Customer"

    rel = model.relationships[0]
    assert rel.identifier == "rel-1"
    assert rel.xml_type == "Serving"
    assert rel.exchange_type == "Serving"
    assert rel.source_id == "app-1"
    assert rel.target_id == "actor-1"
    assert rel.name == "serves"
    assert rel.documentation == "Application serves actor in this model."


def test_parse_exported_xml_fixture():
    xml_path = Path("tests/fixtures/xml/exported-from-graphdb.xml")

    model = parse_archimate_model(xml_path)

    assert len(model.elements) == 2
    assert len(model.relationships) == 1

    app = model.get_element("app-1")
    assert app.xml_type == "ApplicationComponent"
    assert app.name == "My App"
    assert app.documentation == "Application component."

    actor = model.get_element("actor-1")
    assert actor.xml_type == "BusinessActor"
    assert actor.name == "Customer"
    assert actor.documentation == "Business actor."

    rel = model.relationships[0]
    assert rel.identifier == "rel-1"
    assert rel.xml_type == "Serving"
    assert rel.exchange_type == "Serving"
    assert rel.source_id == "app-1"
    assert rel.target_id == "actor-1"
    assert rel.name == "serves"
    assert rel.documentation == "Application serves actor in this model."


def test_parse_supported_technology_elements():
    xml_text = """\
    <model xmlns="http://www.opengroup.org/xsd/archimate/3.0/"
           xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
           identifier="model-1"
           version="1.0">
      <elements>
        <element identifier="node-1" xsi:type="Node">
          <name xml:lang="en">Infra Node</name>
        </element>
        <element identifier="device-1" xsi:type="Device">
          <name xml:lang="en">Server Device</name>
        </element>
        <element identifier="syssoft-1" xsi:type="SystemSoftware">
          <name xml:lang="en">Middleware</name>
        </element>
        <element identifier="techif-1" xsi:type="TechnologyInterface">
          <name xml:lang="en">Tech Interface</name>
        </element>
        <element identifier="techsvc-1" xsi:type="TechnologyService">
          <name xml:lang="en">Tech Service</name>
        </element>
        <element identifier="techcollab-1" xsi:type="TechnologyCollaboration">
          <name xml:lang="en">Tech Collaboration</name>
        </element>
        <element identifier="techevt-1" xsi:type="TechnologyEvent">
          <name xml:lang="en">Tech Event</name>
        </element>
        <element identifier="techfn-1" xsi:type="TechnologyFunction">
          <name xml:lang="en">Tech Function</name>
        </element>
        <element identifier="techint-1" xsi:type="TechnologyInteraction">
          <name xml:lang="en">Tech Interaction</name>
        </element>
        <element identifier="techproc-1" xsi:type="TechnologyProcess">
          <name xml:lang="en">Tech Process</name>
        </element>
        <element identifier="artifact-1" xsi:type="Artifact">
          <name xml:lang="en">Tech Artifact</name>
        </element>
        <element identifier="commnet-1" xsi:type="CommunicationNetwork">
          <name xml:lang="en">Communication Network</name>
        </element>
      </elements>
      <relationships>
        <relationship identifier="rel-1"
                      xsi:type="Realization"
                      source="device-1"
                      target="techsvc-1">
          <name xml:lang="en">realizes</name>
          <documentation xml:lang="en">Device realizes technology service.</documentation>
        </relationship>
        <relationship identifier="rel-2"
                      xsi:type="Aggregation"
                      source="techcollab-1"
                      target="device-1">
          <name xml:lang="en">contains</name>
          <documentation xml:lang="en">Technology collaboration aggregates the device.</documentation>
        </relationship>
        <relationship identifier="rel-3"
                      xsi:type="Access"
                      source="commnet-1"
                      target="techif-1">
          <name xml:lang="en">uses</name>
          <documentation xml:lang="en">Communication network accesses the technology interface.</documentation>
        </relationship>
      </relationships>
    </model>
    """

    model = parse_archimate_model_string(xml_text)

    assert len(model.elements) == 12
    assert len(model.relationships) == 3

    assert model.get_element("node-1").xml_type == "Node"
    assert model.get_element("device-1").xml_type == "Device"
    assert model.get_element("syssoft-1").xml_type == "SystemSoftware"
    assert model.get_element("techif-1").xml_type == "TechnologyInterface"
    assert model.get_element("techsvc-1").xml_type == "TechnologyService"
    assert model.get_element("techcollab-1").xml_type == "TechnologyCollaboration"
    assert model.get_element("techevt-1").xml_type == "TechnologyEvent"
    assert model.get_element("techfn-1").xml_type == "TechnologyFunction"
    assert model.get_element("techint-1").xml_type == "TechnologyInteraction"
    assert model.get_element("techproc-1").xml_type == "TechnologyProcess"
    assert model.get_element("artifact-1").xml_type == "Artifact"
    assert model.get_element("commnet-1").xml_type == "CommunicationNetwork"

    relationship = model.relationships[0]
    assert relationship.xml_type == "Realization"
    assert relationship.source_id == "device-1"
    assert relationship.target_id == "techsvc-1"


def test_parse_supported_physical_elements():
    xml_text = """\
    <model xmlns="http://www.opengroup.org/xsd/archimate/3.0/"
           xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
           identifier="model-1"
           version="1.0">
      <elements>
        <element identifier="equipment-1" xsi:type="Equipment">
          <name xml:lang="en">Production Equipment</name>
        </element>
        <element identifier="facility-1" xsi:type="Facility">
          <name xml:lang="en">Manufacturing Facility</name>
        </element>
        <element identifier="material-1" xsi:type="Material">
          <name xml:lang="en">Raw Material</name>
        </element>
        <element identifier="distribution-1" xsi:type="DistributionNetwork">
          <name xml:lang="en">Plant Distribution Network</name>
        </element>
      </elements>
      <relationships>
        <relationship identifier="rel-1"
                      xsi:type="Access"
                      source="equipment-1"
                      target="material-1">
          <name xml:lang="en">uses</name>
          <documentation xml:lang="en">Equipment accesses raw material.</documentation>
        </relationship>
        <relationship identifier="rel-2"
                      xsi:type="Flow"
                      source="distribution-1"
                      target="equipment-1">
          <name xml:lang="en">flows to</name>
          <documentation xml:lang="en">Distribution network flows to equipment.</documentation>
        </relationship>
      </relationships>
    </model>
    """

    model = parse_archimate_model_string(xml_text)

    assert len(model.elements) == 4
    assert len(model.relationships) == 2

    assert model.get_element("equipment-1").xml_type == "Equipment"
    assert model.get_element("facility-1").xml_type == "Facility"
    assert model.get_element("material-1").xml_type == "Material"
    assert model.get_element("distribution-1").xml_type == "DistributionNetwork"

    assert model.relationships[0].xml_type == "Access"
    assert model.relationships[0].source_id == "equipment-1"
    assert model.relationships[0].target_id == "material-1"
    assert model.relationships[1].xml_type == "Flow"
    assert model.relationships[1].source_id == "distribution-1"
    assert model.relationships[1].target_id == "equipment-1"


def test_parse_supported_motivation_elements():
    xml_text = """\
    <model xmlns="http://www.opengroup.org/xsd/archimate/3.0/"
           xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
           identifier="model-1"
           version="1.0">
      <elements>
        <element identifier="stakeholder-1" xsi:type="Stakeholder">
          <name xml:lang="en">Executive Sponsor</name>
        </element>
        <element identifier="driver-1" xsi:type="Driver">
          <name xml:lang="en">Cost Reduction</name>
        </element>
        <element identifier="goal-1" xsi:type="Goal">
          <name xml:lang="en">Reduce Operational Cost</name>
        </element>
        <element identifier="assessment-1" xsi:type="Assessment">
          <name xml:lang="en">Risk Assessment</name>
        </element>
        <element identifier="principle-1" xsi:type="Principle">
          <name xml:lang="en">Cost Efficiency Principle</name>
        </element>
        <element identifier="constraint-1" xsi:type="Constraint">
          <name xml:lang="en">Budget Constraint</name>
        </element>
        <element identifier="meaning-1" xsi:type="Meaning">
          <name xml:lang="en">Operational Value Meaning</name>
        </element>
        <element identifier="requirement-1" xsi:type="Requirement">
          <name xml:lang="en">Lower Infrastructure Spend</name>
        </element>
        <element identifier="value-1" xsi:type="Value">
          <name xml:lang="en">Sustainable Operations</name>
        </element>
      </elements>
      <relationships>
        <relationship identifier="rel-1"
                      xsi:type="Influence"
                      source="driver-1"
                      target="goal-1">
          <name xml:lang="en">influences</name>
          <documentation xml:lang="en">Driver influences the business goal.</documentation>
        </relationship>
        <relationship identifier="rel-2"
                      xsi:type="Realization"
                      source="requirement-1"
                      target="goal-1">
          <name xml:lang="en">realizes</name>
          <documentation xml:lang="en">Requirement realizes the business goal.</documentation>
        </relationship>
        <relationship identifier="rel-3"
                      xsi:type="Association"
                      source="stakeholder-1"
                      target="goal-1">
          <name xml:lang="en">is interested in</name>
          <documentation xml:lang="en">Stakeholder is associated with the business goal.</documentation>
        </relationship>
      </relationships>
    </model>
    """

    model = parse_archimate_model_string(xml_text)

    assert len(model.elements) == 9
    assert len(model.relationships) == 3

    assert model.get_element("stakeholder-1").xml_type == "Stakeholder"
    assert model.get_element("driver-1").xml_type == "Driver"
    assert model.get_element("goal-1").xml_type == "Goal"
    assert model.get_element("assessment-1").xml_type == "Assessment"
    assert model.get_element("principle-1").xml_type == "Principle"
    assert model.get_element("constraint-1").xml_type == "Constraint"
    assert model.get_element("meaning-1").xml_type == "Meaning"
    assert model.get_element("requirement-1").xml_type == "Requirement"
    assert model.get_element("value-1").xml_type == "Value"

    assert model.relationships[0].xml_type == "Influence"
    assert model.relationships[0].source_id == "driver-1"
    assert model.relationships[0].target_id == "goal-1"
    assert model.relationships[1].xml_type == "Realization"
    assert model.relationships[1].source_id == "requirement-1"
    assert model.relationships[1].target_id == "goal-1"
    assert model.relationships[2].xml_type == "Association"
    assert model.relationships[2].source_id == "stakeholder-1"
    assert model.relationships[2].target_id == "goal-1"


def test_parse_supported_additional_archimate_element_types():
    xml_text = """\
    <model xmlns="http://www.opengroup.org/xsd/archimate/3.0/"
           xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
           identifier="model-1"
           version="1.0">
      <elements>
        <element identifier="capability-1" xsi:type="Capability">
          <name xml:lang="en">Operational Capability</name>
        </element>
        <element identifier="courseofaction-1" xsi:type="CourseOfAction">
          <name xml:lang="en">Transition Plan</name>
        </element>
        <element identifier="deliverable-1" xsi:type="Deliverable">
          <name xml:lang="en">Project Deliverable</name>
        </element>
        <element identifier="gap-1" xsi:type="Gap">
          <name xml:lang="en">Current Capability Gap</name>
        </element>
        <element identifier="grouping-1" xsi:type="Grouping">
          <name xml:lang="en">Stakeholder Group</name>
        </element>
        <element identifier="implementationevent-1" xsi:type="ImplementationEvent">
          <name xml:lang="en">Deployment Event</name>
        </element>
        <element identifier="location-1" xsi:type="Location">
          <name xml:lang="en">Data Center Location</name>
        </element>
        <element identifier="outcome-1" xsi:type="Outcome">
          <name xml:lang="en">Operational Outcome</name>
        </element>
        <element identifier="path-1" xsi:type="Path">
          <name xml:lang="en">Process Path</name>
        </element>
        <element identifier="plateau-1" xsi:type="Plateau">
          <name xml:lang="en">Target Plateau</name>
        </element>
        <element identifier="resource-1" xsi:type="Resource">
          <name xml:lang="en">Operational Resource</name>
        </element>
        <element identifier="valuestream-1" xsi:type="ValueStream">
          <name xml:lang="en">Customer Value Stream</name>
        </element>
        <element identifier="workpackage-1" xsi:type="WorkPackage">
          <name xml:lang="en">Implementation Work Package</name>
        </element>
      </elements>
    </model>
    """

    model = parse_archimate_model_string(xml_text)

    assert len(model.elements) == 13
    assert model.get_element("capability-1").xml_type == "Capability"
    assert model.get_element("courseofaction-1").xml_type == "CourseOfAction"
    assert model.get_element("deliverable-1").xml_type == "Deliverable"
    assert model.get_element("gap-1").xml_type == "Gap"
    assert model.get_element("grouping-1").xml_type == "Grouping"
    assert model.get_element("implementationevent-1").xml_type == "ImplementationEvent"
    assert model.get_element("location-1").xml_type == "Location"
    assert model.get_element("outcome-1").xml_type == "Outcome"
    assert model.get_element("path-1").xml_type == "Path"
    assert model.get_element("plateau-1").xml_type == "Plateau"
    assert model.get_element("resource-1").xml_type == "Resource"
    assert model.get_element("valuestream-1").xml_type == "ValueStream"
    assert model.get_element("workpackage-1").xml_type == "WorkPackage"


def test_parse_model_with_unsupported_element_type_raises():
    xml_text = """\
    <model xmlns="http://www.opengroup.org/xsd/archimate/3.0/"
           xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
           identifier="model-1"
           version="1.0">
      <elements>
        <element identifier="unsupported-1" xsi:type="UnsupportedType">
          <name xml:lang="en">Unsupported Type</name>
        </element>
      </elements>
    </model>
    """

    with pytest.raises(ArchimateXmlParseError) as exc:
        parse_archimate_model_string(xml_text)

    assert "Unsupported element xsi:type 'UnsupportedType'" in str(exc.value)


def test_parse_relationship_without_source_raises():
    xml_text = """\
    <model xmlns="http://www.opengroup.org/xsd/archimate/3.0/"
           xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
           identifier="model-1"
           version="1.0">
      <elements>
        <element identifier="app-1" xsi:type="ApplicationComponent">
          <name xml:lang="en">My App</name>
        </element>
        <element identifier="actor-1" xsi:type="BusinessActor">
          <name xml:lang="en">Customer</name>
        </element>
      </elements>
      <relationships>
        <relationship identifier="rel-1"
                      xsi:type="Serving"
                      target="actor-1">
          <name xml:lang="en">serves</name>
        </relationship>
      </relationships>
    </model>
    """

    with pytest.raises(ArchimateXmlParseError) as exc:
        parse_archimate_model_string(xml_text)

    assert "Missing required attribute 'source'" in str(exc.value)


def test_parse_relationship_without_target_raises():
    xml_text = """\
    <model xmlns="http://www.opengroup.org/xsd/archimate/3.0/"
           xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
           identifier="model-1"
           version="1.0">
      <elements>
        <element identifier="app-1" xsi:type="ApplicationComponent">
          <name xml:lang="en">My App</name>
        </element>
        <element identifier="actor-1" xsi:type="BusinessActor">
          <name xml:lang="en">Customer</name>
        </element>
      </elements>
      <relationships>
        <relationship identifier="rel-1"
                      xsi:type="Serving"
                      source="app-1">
          <name xml:lang="en">serves</name>
        </relationship>
      </relationships>
    </model>
    """

    with pytest.raises(ArchimateXmlParseError) as exc:
        parse_archimate_model_string(xml_text)

    assert "Missing required attribute 'target'" in str(exc.value)
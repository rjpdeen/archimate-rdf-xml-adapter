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


def test_parse_model_with_unsupported_element_type_raises():
    xml_text = """\
    <model xmlns="http://www.opengroup.org/xsd/archimate/3.0/"
           xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
           identifier="model-1"
           version="1.0">
      <elements>
        <element identifier="node-1" xsi:type="Node">
          <name xml:lang="en">Infra Node</name>
        </element>
      </elements>
    </model>
    """

    with pytest.raises(ArchimateXmlParseError) as exc:
        parse_archimate_model_string(xml_text)

    assert "Unsupported element xsi:type 'Node'" in str(exc.value)


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
from archimate_adapter.xml.parser import parse_archimate_model_string


def test_parse_model_with_data_object_and_access():
    xml_text = """\
    <model xmlns="http://www.opengroup.org/xsd/archimate/3.0/"
           xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
           identifier="model-1"
           version="1.0">
      <name xml:lang="en">Demo model</name>
      <elements>
        <element identifier="app-1" xsi:type="ApplicationComponent">
          <name xml:lang="en">Case App</name>
          <documentation xml:lang="en">Application component.</documentation>
        </element>
        <element identifier="data-1" xsi:type="DataObject">
          <name xml:lang="en">Case Record</name>
          <documentation xml:lang="en">Data object containing case data.</documentation>
        </element>
      </elements>
      <relationships>
        <relationship identifier="rel-4"
                      xsi:type="Access"
                      source="app-1"
                      target="data-1">
          <name xml:lang="en">accesses</name>
          <documentation xml:lang="en">Application component accesses data object.</documentation>
        </relationship>
      </relationships>
    </model>
    """

    model = parse_archimate_model_string(xml_text)

    assert len(model.elements) == 2
    assert len(model.relationships) == 1

    app = model.get_element("app-1")
    assert app.xml_type == "ApplicationComponent"
    assert app.name == "Case App"
    assert app.documentation == "Application component."

    data = model.get_element("data-1")
    assert data.xml_type == "DataObject"
    assert data.name == "Case Record"
    assert data.documentation == "Data object containing case data."

    rel = model.relationships[0]
    assert rel.identifier == "rel-4"
    assert rel.xml_type == "Access"
    assert rel.exchange_type == "Access"
    assert rel.source_id == "app-1"
    assert rel.target_id == "data-1"
    assert rel.name == "accesses"
    assert rel.documentation == "Application component accesses data object."
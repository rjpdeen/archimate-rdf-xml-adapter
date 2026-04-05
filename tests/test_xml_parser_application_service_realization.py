from archimate_adapter.xml.parser import parse_archimate_model_string


def test_parse_model_with_application_service_and_realization():
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
        <element identifier="appsvc-1" xsi:type="ApplicationService">
          <name xml:lang="en">Case API</name>
          <documentation xml:lang="en">Application service.</documentation>
        </element>
      </elements>
      <relationships>
        <relationship identifier="rel-3"
                      xsi:type="Realization"
                      source="app-1"
                      target="appsvc-1">
          <name xml:lang="en">realizes</name>
          <documentation xml:lang="en">Application component realizes application service.</documentation>
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

    service = model.get_element("appsvc-1")
    assert service.xml_type == "ApplicationService"
    assert service.name == "Case API"
    assert service.documentation == "Application service."

    rel = model.relationships[0]
    assert rel.identifier == "rel-3"
    assert rel.xml_type == "Realization"
    assert rel.exchange_type == "Realization"
    assert rel.source_id == "app-1"
    assert rel.target_id == "appsvc-1"
    assert rel.name == "realizes"
    assert rel.documentation == "Application component realizes application service."
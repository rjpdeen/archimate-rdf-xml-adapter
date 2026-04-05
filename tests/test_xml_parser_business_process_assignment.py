from archimate_adapter.xml.parser import parse_archimate_model_string


def test_parse_model_with_business_process_and_assignment():
    xml_text = """\
    <model xmlns="http://www.opengroup.org/xsd/archimate/3.0/"
           xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
           identifier="model-1"
           version="1.0">
      <name xml:lang="en">Demo model</name>
      <elements>
        <element identifier="actor-1" xsi:type="BusinessActor">
          <name xml:lang="en">Case Worker</name>
          <documentation xml:lang="en">Responsible business actor.</documentation>
        </element>
        <element identifier="process-1" xsi:type="BusinessProcess">
          <name xml:lang="en">Handle Application</name>
          <documentation xml:lang="en">Business process for handling an application.</documentation>
        </element>
      </elements>
      <relationships>
        <relationship identifier="rel-2"
                      xsi:type="Assignment"
                      source="actor-1"
                      target="process-1">
          <name xml:lang="en">is responsible for</name>
          <documentation xml:lang="en">Actor is assigned to process.</documentation>
        </relationship>
      </relationships>
    </model>
    """

    model = parse_archimate_model_string(xml_text)

    assert len(model.elements) == 2
    assert len(model.relationships) == 1

    actor = model.get_element("actor-1")
    assert actor.xml_type == "BusinessActor"
    assert actor.name == "Case Worker"
    assert actor.documentation == "Responsible business actor."

    process = model.get_element("process-1")
    assert process.xml_type == "BusinessProcess"
    assert process.name == "Handle Application"
    assert process.documentation == "Business process for handling an application."

    rel = model.relationships[0]
    assert rel.identifier == "rel-2"
    assert rel.xml_type == "Assignment"
    assert rel.exchange_type == "Assignment"
    assert rel.source_id == "actor-1"
    assert rel.target_id == "process-1"
    assert rel.name == "is responsible for"
    assert rel.documentation == "Actor is assigned to process."
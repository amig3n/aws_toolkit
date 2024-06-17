import pytest
from mocked_output import *
from instances import extract_tag, apply_coloring

@pytest.fixture
def exemplar_tags_list(): 
    return {
            "Tags":[
                {"Key": "Name", "Value": "db-master1"}, 
                {"Key": "Environment", "Value": "dev"},
                {"Key": "Owner", "Value": "devops"},
                {"Key": "Project", "Value": "db"}
            ]
        }

@pytest.fixture
def exemplar_color_config():
    return {
        'colors': [
            {
                'field': 'Status',
                'values': [
                    {
                        "value": "stopped",
                        "color": "\033[37m"
                    },
                    {
                        "value": "terminated",
                        "color": "\033[31m"
                    }
                ]
            },
        ],
        'default': "\033[39m"
    }


@pytest.fixture
def mock_output():
    return mock_ouput

def test_obtain_tags(exemplar_tags_list):
    assert extract_tag(exemplar_tags_list, "Name") == "db-master1", "incorrect value of Tags.Name, should be db-master1"
    assert extract_tag(exemplar_tags_list, "Environment") == "dev", "incorrect value of Tags.Environment, should be dev"
    assert extract_tag(exemplar_tags_list, "Owner") == "devops", "incorrect value of Tags.Owner, should be devops"
    assert extract_tag(exemplar_tags_list, "Project") == "db", "incorrect value of Tags.Project, should be db"
    assert extract_tag(exemplar_tags_list, "NotExistingTag") == None, "incorrect value of Tags.NotExistingTag, should be None"

def test_describe_instances(mock_output):
    # check tags extraction
    current_instance = mock_output['Reservations'][0]['Instances'][0]
    assert extract_tag(current_instance, "Name") == "db-master1", "incorrect value of Tags.Name, should be db-master1"

    # extract few fields
    assert current_instance.get("Status", None) == "stopped", "incorrect value of status field, should be stopped"
    

def test_apply_coloring(exemplar_color_config):
    """Test applying colors for given records"""
    test_data = [
        {'Status': 'stopped'},
        {'Status': 'terminated'},
        {'Status': 'starging'},
    ]

    tested_records = apply_coloring(exemplar_color_config, test_data)
    assert tested_records[0]['Status'] == "\033[37m" + 'stopped' + "\033[39m", "should be light grey"
    assert tested_records[1]['Status'] == "\033[31m" + 'terminated' + "\033[39m", "should be red"
    assert tested_records[2]['Status'] == "\033[39m" + 'starging' + "\033[39m", "starging field should be defaultly colored"  
"""
Тесты для парсера.
"""
import pytest
from pop_file_reader.parser import Parser, Mission, Wave, Robot, Template

TEST_POP = """
{
    "Mission": {
        "Name": "Test Mission",
        "IsAdvanced": true,
        "Waves": [
            {
                "Id": 1,
                "Description": "First Wave",
                "TotalCount": 10,
                "TotalCurrency": 100,
                "Robots": [
                    {
                        "Name": "Heavy",
                        "Class": "HeavyWeapons",
                        "Health": 300,
                        "Scale": 1.0
                    }
                ]
            }
        ],
        "Templates": {
            "T_TFBot_Heavy": {
                "Name": "Heavy",
                "Class": "HeavyWeapons",
                "Health": 300
            }
        }
    }
}
"""

@pytest.fixture
def parser():
    """Фикстура для создания парсера."""
    return Parser()

def test_parse_mission(parser):
    """Тест парсинга миссии."""
    mission = parser.parse(TEST_POP)
    
    assert isinstance(mission, Mission)
    assert mission.name == "Test Mission"
    assert mission.is_advanced == True
    assert len(mission.waves) == 1
    assert mission.templates is not None

def test_parse_wave(parser):
    """Тест парсинга волны."""
    mission = parser.parse(TEST_POP)
    wave = mission.waves[0]
    
    assert isinstance(wave, Wave)
    assert wave.id == 1
    assert wave.description == "First Wave"
    assert wave.total_count == 10
    assert wave.total_currency == 100
    assert len(wave.robots) == 1

def test_parse_robot(parser):
    """Тест парсинга робота."""
    mission = parser.parse(TEST_POP)
    robot = mission.waves[0].robots[0]
    
    assert isinstance(robot, Robot)
    assert robot.name == "Heavy"
    assert robot.class_name == "HeavyWeapons"
    assert robot.attributes["Health"] == 300
    assert robot.attributes["Scale"] == 1.0

def test_parse_template(parser):
    """Тест парсинга шаблона."""
    mission = parser.parse(TEST_POP)
    template = mission.templates["T_TFBot_Heavy"]
    
    assert isinstance(template, Template)
    assert template.name == "Heavy"
    assert template.attributes["Health"] == 300

def test_parse_invalid_json(parser):
    """Тест обработки некорректного JSON."""
    with pytest.raises(Exception):
        parser.parse("{invalid json}")

def test_parse_missing_required_fields(parser):
    """Тест обработки отсутствующих обязательных полей."""
    # Миссия без имени
    invalid_mission = """
    {
        "Mission": {
            "IsAdvanced": true,
            "Waves": []
        }
    }
    """
    
    with pytest.raises(Exception) as exc_info:
        parser.parse(invalid_mission)
    assert "Mission missing Name" in str(exc_info.value)

    # Волна без ID
    invalid_wave = """
    {
        "Mission": {
            "Name": "Test",
            "Waves": [
                {
                    "Description": "Invalid Wave"
                }
            ]
        }
    }
    """
    
    with pytest.raises(Exception) as exc_info:
        parser.parse(invalid_wave)
    assert "Wave missing Id" in str(exc_info.value)

def test_parse_array_values(parser):
    """Тест парсинга массивов."""
    pop_with_array = """
    {
        "Mission": {
            "Name": "Test",
            "Waves": [
                {
                    "Id": 1,
                    "Robots": [
                        {
                            "Name": "Heavy",
                            "Class": "HeavyWeapons",
                            "Tags": ["tag1", "tag2"],
                            "Items": ["item1", "item2"]
                        }
                    ]
                }
            ]
        }
    }
    """
    
    mission = parser.parse(pop_with_array)
    robot = mission.waves[0].robots[0]
    
    assert isinstance(robot.attributes["Tags"], list)
    assert len(robot.attributes["Tags"]) == 2
    assert isinstance(robot.attributes["Items"], list)
    assert len(robot.attributes["Items"]) == 2

def test_parse_nested_blocks(parser):
    """Тест парсинга вложенных блоков."""
    pop_with_nested = """
    {
        "Mission": {
            "Name": "Test",
            "Waves": [
                {
                    "Id": 1,
                    "Robots": [
                        {
                            "Name": "Heavy",
                            "Class": "HeavyWeapons",
                            "Attributes": {
                                "Damage": 150,
                                "Effects": {
                                    "Fire": true,
                                    "Duration": 5
                                }
                            }
                        }
                    ]
                }
            ]
        }
    }
    """
    
    mission = parser.parse(pop_with_nested)
    robot = mission.waves[0].robots[0]
    attributes = robot.attributes["Attributes"]
    
    assert isinstance(attributes, dict)
    assert attributes["Damage"] == 150
    assert isinstance(attributes["Effects"], dict)
    assert attributes["Effects"]["Fire"] == True
    assert attributes["Effects"]["Duration"] == 5

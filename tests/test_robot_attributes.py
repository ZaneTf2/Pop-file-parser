"""
Тесты для проверки работы с атрибутами роботов.
"""
import pytest
from pop_file_reader import PopFileCompiler, Robot, Wave

def test_multiple_items():
    """Тест для множественных предметов."""
    robot = Robot(
        name="Multi-Item Robot",
        class_name="Soldier",
        items=["The Liberty Launcher", "The Gunboats", "The Market Gardener"]
    )
    result = robot.to_valve_format()
    
    # Проверяем что каждый Item на отдельной строке
    assert "Item" in result
    items = result["Item"]
    assert isinstance(items, list)
    assert len(items) == 3
    assert items[0] == "The Liberty Launcher"
    assert items[1] == "The Gunboats"
    assert items[2] == "The Market Gardener"

def test_multiple_attributes():
    """Тест для множественных атрибутов."""
    robot = Robot(
        name="Multi-Attribute Robot",
        class_name="Heavy",
        attributes={"Attributes": ["MiniBoss", "UseBossHealthBar", "SpawnWithFullCharge"]}
    )
    result = robot.to_valve_format()
    
    # Проверяем что Attributes это список
    assert "Attributes" in result
    attrs = result["Attributes"]
    assert isinstance(attrs, list)
    assert len(attrs) == 3
    assert "MiniBoss" in attrs
    assert "UseBossHealthBar" in attrs
    assert "SpawnWithFullCharge" in attrs

def test_item_attributes_with_name():
    """Тест для ItemAttributes с указанным ItemName."""
    robot = Robot(
        name="Item Attributes Robot",
        class_name="Pyro",
        items=["The Phlogistinator"],
        attributes={
            "ItemAttributes": {
                "ItemName": "The Phlogistinator",
                "damage bonus": 1.3,
                "flame life bonus": 2.0
            }
        }
    )
    result = robot.to_valve_format()
    
    # Проверяем ItemAttributes
    assert "ItemAttributes" in result
    item_attrs = result["ItemAttributes"]
    assert isinstance(item_attrs, dict)
    assert item_attrs["ItemName"] == "The Phlogistinator"
    assert item_attrs["damage bonus"] == 1.3
    assert item_attrs["flame life bonus"] == 2.0

def test_item_attributes_without_name():
    """Тест для ItemAttributes без ItemName."""
    robot = Robot(
        name="Default Item Attributes Robot",
        class_name="Heavy",
        items=["The Huo Long Heater"],
        attributes={
            "ItemAttributes": {
                "damage bonus": 1.5,
                "ring of fire while aiming": 20
            }
        }
    )
    result = robot.to_valve_format()
    
    # Проверяем что ItemName добавлен автоматически
    assert "ItemAttributes" in result
    assert result["ItemAttributes"]["ItemName"] == "The Huo Long Heater"

def test_multiple_item_attributes():
    """Тест для нескольких ItemAttributes блоков."""
    robot = Robot(
        name="Multi ItemAttributes Robot",
        class_name="Soldier",
        items=["The Liberty Launcher", "The Market Gardener"],
        attributes={
            "ItemAttributes": [
                {
                    "ItemName": "The Liberty Launcher",
                    "damage bonus": 1.25,
                    "faster reload rate": 0.8
                },
                {
                    "ItemName": "The Market Gardener",
                    "damage bonus": 2.0,
                    "critboost on kill": 3
                }
            ]
        }
    )
    result = robot.to_valve_format()
    
    # Проверяем что все ItemAttributes на месте
    assert "ItemAttributes" in result
    attrs = result["ItemAttributes"]
    assert isinstance(attrs, list)
    assert len(attrs) == 2
    
    # Проверяем первый блок
    assert attrs[0]["ItemName"] == "The Liberty Launcher"
    assert attrs[0]["damage bonus"] == 1.25
    
    # Проверяем второй блок
    assert attrs[1]["ItemName"] == "The Market Gardener"
    assert attrs[1]["damage bonus"] == 2.0

def test_invalid_item_attributes():
    """Тест для ItemAttributes с несуществующим предметом."""
    robot = Robot(
        name="Invalid ItemAttributes Robot",
        class_name="Heavy",
        items=["The Huo Long Heater"],
        attributes={
            "ItemAttributes": {
                "ItemName": "Non-existent Item",
                "damage bonus": 1.5
            }
        }
    )
    result = robot.to_valve_format()
    
    # Проверяем что ItemAttributes не добавлен
    assert "ItemAttributes" not in result

def test_character_attributes():
    """Тест для CharacterAttributes."""
    robot = Robot(
        name="Character Attributes Robot",
        class_name="Scout",
        character_attributes={
            "move speed bonus": 1.4,
            "damage bonus": 1.25,
            "fire rate bonus": 0.8
        }
    )
    result = robot.to_valve_format()
    
    # Проверяем CharacterAttributes
    assert "CharacterAttributes" in result
    attrs = result["CharacterAttributes"]
    assert isinstance(attrs, dict)
    assert attrs["move speed bonus"] == 1.4
    assert attrs["damage bonus"] == 1.25
    assert attrs["fire rate bonus"] == 0.8

def test_export_format():
    """Тест правильности форматирования при экспорте."""
    compiler = PopFileCompiler()
    
    # Создаем тестового робота
    robot = {
        "Name": "Format Test Robot",
        "Class": "Soldier",
        "Item": ["The Liberty Launcher", "The Gunboats"],
        "Attributes": ["MiniBoss", "UseBossHealthBar"],
        "ItemAttributes": {
            "ItemName": "The Liberty Launcher",
            "damage bonus": 1.25
        },
        "CharacterAttributes": {
            "move speed bonus": 1.2
        }
    }
    
    # Создаем волну и добавляем робота
    wave = Wave()
    compiler.add_wave(wave)
    compiler.add_robot(1, robot)
    
    # Экспортируем во временный файл
    import tempfile
    with tempfile.NamedTemporaryFile(suffix=".pop", delete=False) as tmp:
        compiler.export(tmp.name)
        
        # Читаем файл и проверяем форматирование
        with open(tmp.name, "r") as f:
            content = f.read()
            
            # Проверяем форматирование предметов
            assert 'Item "The Liberty Launcher"' in content
            assert 'Item "The Gunboats"' in content
            
            # Проверяем форматирование атрибутов
            assert 'Attributes "MiniBoss"' in content
            assert 'Attributes "UseBossHealthBar"' in content
            
            # Проверяем ItemAttributes
            assert "ItemAttributes" in content
            assert "ItemName The Liberty Launcher" in content
            assert '"damage bonus" 1.25' in content
            
            # Проверяем CharacterAttributes
            assert "CharacterAttributes" in content
            assert '"move speed bonus" 1.2' in content

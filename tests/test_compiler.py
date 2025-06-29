"""
Тесты для компилятора pop файлов.
"""
import pytest
from pathlib import Path
from pop_file_reader import PopFileCompiler, Robot, Wave

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
def compiler():
    """Фикстура для создания компилятора."""
    return PopFileCompiler()

@pytest.fixture
def tmp_pop_file(tmp_path):
    """Фикстура для создания временного pop файла."""
    pop_file = tmp_path / "test.pop"
    pop_file.write_text(TEST_POP)
    return pop_file

def test_load_file(compiler, tmp_pop_file):
    """Тест загрузки файла."""
    compiler.load_file(tmp_pop_file)
    
    assert compiler.mission_name == "Test Mission"
    assert compiler.is_advanced == True
    assert len(compiler.waves) == 1
    assert len(compiler.templates) == 1

def test_validate_valid_file(compiler, tmp_pop_file):
    """Тест валидации корректного файла."""
    compiler.load_file(tmp_pop_file)
    assert compiler.validate() == True

def test_modify_wave(compiler, tmp_pop_file):
    """Тест модификации волны."""
    compiler.load_file(tmp_pop_file)
    
    # Изменяем параметры первой волны
    compiler.modify_wave(1, {
        "totalcount": 20,
        "totalcurrency": 200
    })
    
    wave = next(w for w in compiler.waves if w.id == 1)
    assert wave.totalcount == 20
    assert wave.totalcurrency == 200

def test_add_robot(compiler, tmp_pop_file):
    """Тест добавления робота."""
    compiler.load_file(tmp_pop_file)
    
    # Добавляем нового робота
    robot_config = {
        "Name": "Scout",
        "Class": "Scout",
        "Health": 125,
        "Scale": 1.0
    }
    
    compiler.add_robot(1, robot_config)
    
    wave = next(w for w in compiler.waves if w.id == 1)
    assert len(wave.robots) == 2
    
    new_robot = wave.robots[-1]
    assert new_robot.name == "Scout"
    assert new_robot.class_name == "Scout"
    assert new_robot.health == 125

def test_export(compiler, tmp_pop_file, tmp_path):
    """Тест экспорта файла."""
    compiler.load_file(tmp_pop_file)
    
    # Экспортируем в новый файл
    output_file = tmp_path / "output.pop"
    compiler.export(output_file)
    
    # Проверяем, что файл создан
    assert output_file.exists()
    
    # Загружаем экспортированный файл
    new_compiler = PopFileCompiler()
    new_compiler.load_file(output_file)
    
    # Проверяем содержимое
    assert new_compiler.mission_name == "Test Mission"
    assert new_compiler.is_advanced == True
    assert len(new_compiler.waves) == 1
    assert len(new_compiler.templates) == 1

def test_invalid_wave_id(compiler, tmp_pop_file):
    """Тест обработки некорректного ID волны."""
    compiler.load_file(tmp_pop_file)
    
    with pytest.raises(ValueError):
        compiler.modify_wave(999, {"totalcount": 20})

def test_duplicate_wave_ids(compiler):
    """Тест на дублирование ID волн."""
    wave1 = Wave(id=1, robots=[])
    wave2 = Wave(id=1, robots=[])
    
    compiler.waves = [wave1, wave2]
    assert compiler.validate() == False

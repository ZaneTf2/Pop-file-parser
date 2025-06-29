"""
Тесты для функционала информации о миссии.
"""
import os
import tempfile
from pathlib import Path
import pytest
from pop_file_reader import PopFileCompiler, Robot, Wave, WaveSpawn

def test_set_mission_info():
    compiler = PopFileCompiler()
    
    # Проверяем установку базовой информации
    compiler.set_mission_info(
        mission_name="Test Mission",
        starting_currency=1000,
        respawn_wave_time=6,
        base_files=["robot_standard.pop"]
    )
    
    assert compiler.mission_name == "Test Mission"
    assert compiler.starting_currency == 1000
    assert compiler.respawn_wave_time == 6
    assert compiler.base_files == ["robot_standard.pop"]
    
def test_export_with_mission_info():
    compiler = PopFileCompiler()
    
    # Устанавливаем информацию о миссии
    compiler.set_mission_info(
        mission_name="Export Test",
        starting_currency=800,
        respawn_wave_time=8,
        base_files=["robot_standard.pop", "robot_giant.pop"]
    )
    
    # Добавляем тестовую волну
    wave = Wave()
    spawn = WaveSpawn()
    robot = Robot(
        name="Giant Heavy",
        class_name="HeavyWeapons",
        health=5000,
        skill="Expert"
    )
    spawn.squad.append(robot)
    wave.wave_spawns.append(spawn)
    compiler.waves.append(wave)
    
    # Экспортируем во временный файл
    with tempfile.NamedTemporaryFile(suffix='.pop', delete=False) as tmp:
        tmp_path = Path(tmp.name)
        
    try:
        compiler.export_to_file(tmp_path)
        
        # Проверяем содержимое файла
        with open(tmp_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Проверяем наличие всех ключевых элементов
        assert '#base "robot_standard.pop"' in content
        assert '#base "robot_giant.pop"' in content
        assert '"Name" "Export Test"' in content
        assert '"StartingCurrency" "800"' in content
        assert '"RespawnWaveTime" "8"' in content
        assert '"Class" "HeavyWeapons"' in content
        assert '"Health" "5000"' in content
        
    finally:
        # Удаляем временный файл
        os.unlink(tmp_path)

def test_partial_mission_info():
    compiler = PopFileCompiler()
    
    # Проверяем частичную установку параметров
    compiler.set_mission_info(mission_name="Partial Test")
    assert compiler.mission_name == "Partial Test"
    assert compiler.starting_currency is None
    
    compiler.set_mission_info(starting_currency=500)
    assert compiler.mission_name == "Partial Test"  # Не должно измениться
    assert compiler.starting_currency == 500
    
def test_export_empty_mission():
    compiler = PopFileCompiler()
    
    # Проверяем экспорт без установки информации
    with tempfile.NamedTemporaryFile(suffix='.pop', delete=False) as tmp:
        tmp_path = Path(tmp.name)
        
    try:
        compiler.export_to_file(tmp_path)
        
        # Проверяем, что файл создан и пустой
        with open(tmp_path, 'r', encoding='utf-8') as f:
            content = f.read().strip()
            
        assert content == "{}"  # Пустой файл должен содержать только пустой объект
        
    finally:
        os.unlink(tmp_path)

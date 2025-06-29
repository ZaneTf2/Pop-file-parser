"""Тесты для проверки корректности формата экспорта."""
import os
import unittest
from pop_file_reader.compiler import PopFileCompiler
from pop_file_reader.models.wave import Wave
from pop_file_reader.models.wave_spawn import WaveSpawn
from pop_file_reader.models.tf_bot import TFBot

class TestExportFormat(unittest.TestCase):
    def setUp(self):
        self.compiler = PopFileCompiler()
        self.output_file = "test_output.pop"
        
    def tearDown(self):
        if os.path.exists(self.output_file):
            os.remove(self.output_file)
            
    def test_wave_spawn_structure(self):
        """Проверяет структуру WaveSpawn без лишних блоков."""
        wave = Wave()
        spawn = WaveSpawn()
        spawn.name = "Test Wave"
        spawn.total_count = 10
        spawn.max_active = 5
        spawn.where = "spawnbot"
        
        bot = TFBot()
        bot.name = "Test Bot"
        bot.class_name = "Heavy"
        bot.health = 300
        bot.attributes = ["AlwaysCrit"]
        
        spawn.squad.append(bot)
        wave.wave_spawns.append(spawn)
        self.compiler.waves.append(wave)
        
        self.compiler.export_to_file(self.output_file)
        
        with open(self.output_file, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Проверяем отсутствие пустых блоков
        self.assertNotIn('""', content)
        # Проверяем структуру Attributes
        self.assertIn('"Attributes" "AlwaysCrit"', content)
        # Проверяем числа без кавычек
        self.assertIn('"Health" 300', content)
        
    def test_item_attributes_format(self):
        """Проверяет формат ItemAttributes с кавычками для ItemName."""
        wave = Wave()
        spawn = WaveSpawn()
        bot = TFBot()
        bot.name = "Scout"
        bot.class_name = "Scout"
        bot.items = ["Force-A-Nature"]
        bot.item_attributes = {
            "ItemName": "Force-A-Nature",
            "clip size bonus": 1.5
        }
        
        spawn.squad.append(bot)
        wave.wave_spawns.append(spawn)
        self.compiler.waves.append(wave)
        
        self.compiler.export_to_file(self.output_file)
        
        with open(self.output_file, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Проверяем ItemName в кавычках
        self.assertIn('"ItemName" "Force-A-Nature"', content)
        # Проверяем числовые атрибуты без кавычек
        self.assertIn('"clip size bonus" 1.5', content)
        
    def test_mission_params_no_duplication(self):
        """Проверяет отсутствие дублирования параметров в Mission."""
        self.compiler.starting_currency = 1000
        self.compiler.respawn_wave_time = 5
        self.compiler.additional_params = {
            "FixedRespawnWaveTime": True,
            "Advanced": 1
        }
        
        self.compiler.export_to_file(self.output_file)
        
        with open(self.output_file, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Проверяем, что параметры есть только в Mission
        wave_schedule_count = content.count('"StartingCurrency"')
        self.assertEqual(wave_schedule_count, 1)
        
        # Проверяем булевы значения
        self.assertIn('"FixedRespawnWaveTime" "Yes"', content)
        
    def test_base_files_with_quotes(self):
        """Проверяет корректное форматирование base директив."""
        self.compiler.base_files = ["robot_standard.pop", "robot_giant.pop"]
        self.compiler.export_to_file(self.output_file)
        
        with open(self.output_file, 'r', encoding='utf-8') as f:
            content = f.read().splitlines()
            
        # Проверяем base директивы в начале файла
        self.assertIn('#base "robot_standard.pop"', content[0])
        self.assertIn('#base "robot_giant.pop"', content[1])
        
if __name__ == '__main__':
    unittest.main()

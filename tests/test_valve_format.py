"""
Тесты для проверки корректности формата экспорта.
"""
import os
import unittest
from pop_file_reader.compiler import PopFileCompiler
from pop_file_reader.models.wave import Wave
from pop_file_reader.models.wave_spawn import WaveSpawn
from pop_file_reader.models.tf_bot import TFBot

class TestValveFormat(unittest.TestCase):
    def setUp(self):
        self.compiler = PopFileCompiler()
        self.output_file = "test_valve_format.pop"
        
    def tearDown(self):
        if os.path.exists(self.output_file):
            os.remove(self.output_file)
            
    def test_format_matches_valve(self):
        """Проверяет соответствие формату Valve."""
        # Добавляем base файлы
        self.compiler.base_files = ["robot_giant.pop", "robot_standard.pop"]
        
        # Добавляем основные параметры
        self.compiler.starting_currency = 1000
        self.compiler.respawn_wave_time = 5
        self.compiler.additional_params.update({
            "CanBotsAttackWhileInSpawnRoom": False,
            "FixedRespawnWaveTime": True,
            "Advanced": 1
        })
        
        # Создаем волну со скаутами
        wave = Wave()
        spawn = WaveSpawn()
        spawn.name = "Scout Rush"
        spawn.total_count = 24
        spawn.max_active = 8
        spawn.spawn_count = 4
        spawn.wait_between_spawns = 2
        spawn.where = "spawnbot"
        spawn.total_currency = 200
        spawn.random_spawn = True
        
        bot = TFBot()
        bot.name = "Fast Scout"
        bot.class_name = "Scout"
        bot.health = 175
        bot.skill = "Hard"
        bot.attributes = ["AlwaysCrit"]
        bot.character_attributes = {
            "move speed bonus": 1.3,
            "damage bonus": 1.2
        }
        bot.items = ["Force-A-Nature"]
        bot.item_attributes = {
            "clip size bonus": 1.5,
            "ItemName": "Force-A-Nature"
        }
        
        spawn.squad.append(bot)
        wave.wave_spawns.append(spawn)
        self.compiler.waves.append(wave)
        
        self.compiler.export_to_file(self.output_file)
        
        with open(self.output_file, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Проверяем формат
        # Base директивы
        self.assertIn('#base robot_giant.pop', content)
        self.assertIn('#base robot_standard.pop', content)
        
        # Параметры без кавычек (целые числа)
        self.assertIn('StartingCurrency 1000', content)
        self.assertIn('RespawnWaveTime 5', content)
        self.assertIn('TotalCount 24', content)
        self.assertIn('MaxActive 8', content)
        
        # Параметры в кавычках (строки)
        self.assertIn('Where "spawnbot"', content)
        self.assertIn('Name "Scout Rush"', content)
        self.assertIn('Class "Scout"', content)
        
        # Параметры булевые
        self.assertIn('RandomSpawn 1', content)
        self.assertIn('FixedRespawnWaveTime Yes', content)
        
        # Атрибуты
        self.assertIn('Attributes "AlwaysCrit"', content)
        
        # ItemAttributes
        self.assertIn('ItemName "Force-A-Nature"', content)
        self.assertIn('clip size bonus 1.5', content)
        
        # CharacterAttributes без кавычек для чисел
        self.assertIn('move speed bonus 1.3', content)
        self.assertIn('damage bonus 1.2', content)

if __name__ == '__main__':
    unittest.main()

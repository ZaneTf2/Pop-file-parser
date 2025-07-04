"""
Тесты для проверки форматирования значений в .pop файлах.
"""
import os
import unittest
from pop_file_parser.compiler import PopFileCompiler
from pop_file_parser.models.wave import Wave
from pop_file_parser.models.wave_spawn import WaveSpawn
from pop_file_parser.models.tf_bot import TFBot

class TestValueFormatting(unittest.TestCase):
    def setUp(self):
        self.compiler = PopFileCompiler()
        self.output_file = "test_formatting.pop"
        
    def tearDown(self):
        if os.path.exists(self.output_file):
            os.remove(self.output_file)
            
    def test_boolean_formatting(self):
        """Проверяет форматирование булевых значений."""
        self.compiler.additional_params.update({
            "FixedRespawnWaveTime": True,
            "CanBotsAttackWhileInSpawnRoom": False
        })
        
        # Wave с поддержкой
        wave = Wave()
        spawn = WaveSpawn()
        spawn.support = True
        spawn.random_spawn = True
        wave.wave_spawns.append(spawn)
        self.compiler.waves.append(wave)
        
        self.compiler.export_to_file(self.output_file)
        
        with open(self.output_file, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Проверяем Yes/No для корневых параметров
        self.assertIn('FixedRespawnWaveTime Yes', content)
        self.assertIn('CanBotsAttackWhileInSpawnRoom No', content)
        
        # Проверяем 1/0 для параметров внутри Wave
        self.assertIn('Support 1', content)
        self.assertIn('RandomSpawn 1', content)
        
    def test_attributes_formatting(self):
        """Проверяет форматирование атрибутов."""
        wave = Wave()
        spawn = WaveSpawn()
        
        bot = TFBot()
        bot.name = "Test Bot"
        bot.attributes = ["UseBossHealthBar", "AlwaysCrit"]
        bot.items = ["The Kritzkrieg"]
        bot.item_attributes = {
            "ItemName": "The Kritzkrieg",
            "heal rate bonus": 1.5,
            "ubercharge rate bonus": 2.0
        }
        bot.character_attributes = {
            "move speed bonus": 1.3,
            "damage bonus": 1.2
        }
        
        spawn.squad.append(bot)
        wave.wave_spawns.append(spawn)
        self.compiler.waves.append(wave)
        
        self.compiler.export_to_file(self.output_file)
        
        with open(self.output_file, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Проверяем Attributes без кавычек
        self.assertIn('Attributes UseBossHealthBar AlwaysCrit', content)
        
        # Проверяем форматирование ItemAttributes
        self.assertIn('ItemName "The Kritzkrieg"', content)
        self.assertIn('"heal rate bonus" 1.5', content)
        self.assertIn('"ubercharge rate bonus" 2', content)
        
        # Проверяем форматирование CharacterAttributes
        self.assertIn('"move speed bonus" 1.3', content)
        self.assertIn('"damage bonus" 1.2', content)

if __name__ == '__main__':
    unittest.main()

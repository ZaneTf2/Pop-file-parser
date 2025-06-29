"""
Тесты для проверки поддержки комментариев и дополнительных параметров.
"""
import os
import unittest
from pop_file_reader.compiler import PopFileCompiler
from pop_file_reader.models.wave import Wave
from pop_file_reader.models.wave_spawn import WaveSpawn
from pop_file_reader.models.tf_bot import TFBot

class TestCommentsAndParams(unittest.TestCase):
    def setUp(self):
        self.compiler = PopFileCompiler()
        self.output_file = "test_output.pop"
        
    def tearDown(self):
        if os.path.exists(self.output_file):
            os.remove(self.output_file)
            
    def test_base_files_with_quotes(self):
        """Проверяет, что base директивы корректно записываются с кавычками."""
        self.compiler.base_files = ["robot_standard.pop", "robot_giant.pop"]
        self.compiler.export_to_file(self.output_file)
        
        with open(self.output_file, 'r', encoding='utf-8') as f:
            content = f.read()
            
        self.assertIn('#base "robot_standard.pop"', content)
        self.assertIn('#base "robot_giant.pop"', content)
        
    def test_comments_in_blocks(self):
        """Проверяет поддержку комментариев для блоков."""
        wave = Wave()
        spawn = WaveSpawn()
        bot = TFBot()
        bot.name = "Heavy"
        spawn.squad.append(bot)
        wave.wave_spawns.append(spawn)
        self.compiler.waves.append(wave)
        
        # Добавляем комментарии
        self.compiler.add_comment("Wave1", "Первая волна с Heavy")
        self.compiler.add_comment("Mission", "Основная миссия")
        
        # Добавляем информацию о миссии
        self.compiler.mission_info = {
            "Objective": "Defend",
            "Where": "spawnbot"
        }
        
        self.compiler.export_to_file(self.output_file)
        
        with open(self.output_file, 'r', encoding='utf-8') as f:
            content = f.read()
            
        self.assertIn('// Первая волна с Heavy', content)
        self.assertIn('// Основная миссия', content)
        self.assertIn('"Where" "spawnbot"', content)
        
    def test_additional_parameters(self):
        """Проверяет поддержку дополнительных параметров."""
        self.compiler.set_checkpoint("reached_checkpoint")
        self.compiler.set_sound("MVM.RobotSpawn")
        self.compiler.add_param("FixedRespawnWaveTime", 1)
        
        wave = Wave()
        self.compiler.waves.append(wave)
        
        self.compiler.export_to_file(self.output_file)
        
        with open(self.output_file, 'r', encoding='utf-8') as f:
            content = f.read()
            
        self.assertIn('"Checkpoint" "reached_checkpoint"', content)
        self.assertIn('"Sound" "MVM.RobotSpawn"', content)
        self.assertIn('"FixedRespawnWaveTime" 1', content)
        
if __name__ == '__main__':
    unittest.main()

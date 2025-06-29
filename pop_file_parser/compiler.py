"""
Основной модуль компилятора pop файлов.
"""
from pathlib import Path
from typing import Dict, List, Optional, Union, Any
import logging
from .valve_parser import ValveFormat
from .models.wave import Wave
from .models.wave_spawn import WaveSpawn
from .models.tf_bot import TFBot

logger = logging.getLogger(__name__)

from .models.mission import Mission
from .models.template import TemplateManager, Template

class PopFileCompiler:
    """Компилятор pop файлов для MvM режима Team Fortress 2."""
    def __init__(self):
        """Инициализирует компилятор."""
        self.waves: List[Wave] = []
        self.base_files: List[str] = []  # Пустой список, файлы добавляются явно
        self.mission: Dict[str, Any] = {"WaveSchedule": {}}  # Основная структура миссии
        self.missions: List[Mission] = []  # Список поддерживающих миссий
        self.template_manager = TemplateManager()  # Менеджер шаблонов
        self.comments: Dict[str, str] = {}  # Комментарии для блоков
        
    def add_robot(self, wave_id: int, robot_config: dict) -> None:
        """Добавляет нового робота в волну."""
        if not 1 <= wave_id <= len(self.waves):
            raise ValueError(f"Wave {wave_id} not found")
            
        wave = self.waves[wave_id - 1]
        if not wave.wave_spawns:
            wave.wave_spawns.append(WaveSpawn())
            
        robot = TFBot.from_valve_format(robot_config)
        wave.wave_spawns[0].squad.append(robot)

    def export_to_file(self, file_path: Union[str, Path]) -> None:
        """
        Экспортирует миссию в .pop файл.
        
        Args:
            file_path: Путь для сохранения файла
        """
        parser = ValveFormat()
        output = self.mission

        # Добавляем уникальные base директивы если они есть
        if self.base_files:
            unique_bases = list(dict.fromkeys(self.base_files))
            output["__base_files"] = unique_bases

        # Добавляем миссии и шаблоны в основную структуру
        wave_schedule = output.get("WaveSchedule", {})
        wave_schedule.update(self._compile_missions())
        wave_schedule.update(self._compile_templates())
        output["WaveSchedule"] = wave_schedule

        with open(file_path, 'w', encoding='utf-8') as f:
            # Сначала #base директивы
            if "__base_files" in output:
                for base_file in output["__base_files"]:
                    f.write(f'#base {base_file}\n')
                f.write('\n')
                del output["__base_files"]

            # Затем основное содержимое
            f.write(parser.dump(output))

    def get_wave(self, wave_id: int) -> Optional[Wave]:
        """Возвращает объект волны по номеру (1-индексация)."""
        if 1 <= wave_id <= len(self.waves):
            return self.waves[wave_id - 1]
        return None

    def get_wave_spawn(self, wave_id: int, spawn_index: int = 0) -> Optional[WaveSpawn]:
        """Возвращает объект Squad по индексу (0-индексация)."""
        wave = self.get_wave(wave_id)
        if wave and 0 <= spawn_index < len(wave.wave_spawns):
            return wave.wave_spawns[spawn_index]
        return None

    def get_robots(self, wave_id: int, spawn_index: int = 0) -> List[TFBot]:
        """Возвращает список роботов в указанном спавне волны."""
        spawn = self.get_wave_spawn(wave_id, spawn_index)
        if spawn:
            return spawn.squad
        return []

    def edit_robot(self, wave_id: int, robot_index: int, new_data: dict, spawn_index: int = 0) -> None:
        """Редактирует параметры робота по индексу в спавне."""
        robots = self.get_robots(wave_id, spawn_index)
        if 0 <= robot_index < len(robots):
            robot = robots[robot_index]
            for key, value in new_data.items():
                if hasattr(robot, key):
                    setattr(robot, key, value)
                else:
                    robot.attributes[key] = value
        else:
            raise IndexError(f"Robot index {robot_index} out of range for wave {wave_id}")

    def remove_robot(self, wave_id: int, robot_index: int, spawn_index: int = 0) -> None:
        """Удаляет робота по индексу из спавна."""
        robots = self.get_robots(wave_id, spawn_index)
        if 0 <= robot_index < len(robots):
            del robots[robot_index]
        else:
            raise IndexError(f"Robot index {robot_index} out of range for wave {wave_id}")

    def add_wave(self, wave: Optional[Wave] = None) -> None:
        """Добавляет новую волну (можно передать готовый объект или создать пустую)."""
        if wave is None:
            wave = Wave()
        self.waves.append(wave)

    def add_global_settings(self, settings: Dict[str, Any]) -> None:
        """
        Добавляет глобальные настройки в миссию.
        
        Args:
            settings: Словарь с настройками миссии
        """
        self.mission["WaveSchedule"].update(settings)

    def add_wave_spawn(self, wave_id: int, spawn: Optional[WaveSpawn] = None) -> None:
        """Добавляет новый Squad в указанную волну."""
        wave = self.get_wave(wave_id)
        if wave:
            if spawn is None:
                spawn = WaveSpawn()
            wave.wave_spawns.append(spawn)
        else:
            raise ValueError(f"Wave {wave_id} not found")

    def add_comment(self, block_id: str, comment: str) -> None:
        """Добавляет комментарий к блоку."""
        self.comments[block_id] = comment

    def set_checkpoint(self, checkpoint: str) -> None:
        """Устанавливает параметр Checkpoint."""
        self.checkpoint = checkpoint

    def set_sound(self, sound: str) -> None:
        """Устанавливает параметр Sound."""
        self.sound = sound

    def add_param(self, name: str, value: Any) -> None:
        """Добавляет дополнительный параметр из mvm.txt."""
        self.additional_params[name] = value

    def add_wave(self, wave: Wave) -> None:
        """
        Добавляет волну в миссию.
        
        Args:
            wave: Объект Wave для добавления
        """
        if "Wave" not in self.mission["WaveSchedule"]:
            self.mission["WaveSchedule"]["Wave"] = []
        
        self.mission["WaveSchedule"]["Wave"].append(wave.to_valve_format())

    def add_template(self, name: str, bot: TFBot, comments: str = "") -> None:
        """
        Добавляет шаблон робота.
        
        Args:
            name: Имя шаблона
            bot: Объект TFBot
            comments: Комментарии к шаблону
        """
        self.template_manager.add_template(name, bot, comments)

    def get_template(self, name: str) -> Optional[Template]:
        """
        Получает шаблон по имени.
        
        Args:
            name: Имя шаблона
        """
        return self.template_manager.get_template(name)

    def add_mission(self, mission: Mission) -> None:
        """Добавляет поддерживающую миссию."""
        self.missions.append(mission)
        
    def _compile_missions(self) -> Dict[str, Any]:
        """Компилирует все поддерживающие миссии."""
        result = {}
        if self.missions:
            result["Mission"] = [mission.to_valve_format() for mission in self.missions]
        return result
        
    def _compile_templates(self) -> Dict[str, Any]:
        """Компилирует все шаблоны."""
        result = {}
        if self.template_manager.templates:
            result["Templates"] = self.template_manager.to_valve_format()
        return result

"""
Модель для представления волны в MvM миссии.
"""
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional
from .wave_spawn import WaveSpawn
from .tank import Tank
from .output_block import OutputBlock
from .base import CommentableMixin

@dataclass
class Wave(CommentableMixin):
    """Представляет волну в MvM миссии."""
    wave_spawns: List[Any] = field(default_factory=list)
    tanks: List[Any] = field(default_factory=list)
    wait_when_done: int = 0
    checkpoint: bool = False
    start_wave_output: Optional[Any] = None
    done_output: Optional[Any] = None
    init_wave_output: Optional[Any] = None
    custom_outputs: List[Any] = field(default_factory=list)
    # comment унаследован и уже идёт с дефолтом

    def add_custom_output(self, name: str, target: str = "", action: str = "", custom_settings: Any = "") -> None:
        """
        Добавляет пользовательский output блок.
        
        Args:
            name: Имя блока (например, 'TankDeathOutput' или 'Parameters')
            target: Цель (например, 'wave_tank_spawn')
            action: Действие (например, 'Trigger')
            custom_settings: Дополнительные настройки. 
                           Для Parameters может быть словарем или строкой в формате Valve.
        """
        # Создаем блок в зависимости от типа
        if name == "Parameters":
            # Для Parameters принимаем как словарь, так и строку
            output = OutputBlock(name=name, custom_settings=custom_settings)
        else:
            # Для обычных output блоков
            output = OutputBlock(name=name, target=target, action=action, custom_settings=custom_settings)
        
        self.custom_outputs.append(output)
    
    def to_valve_format(self) -> Dict[str, Any]:
        """Конвертирует волну в формат Valve."""
        result = {}
        
        # Добавляем комментарий если он есть
        if self.comment:
            result["__comment"] = self.comment
        
        # Добавляем основные параметры
        if self.wait_when_done:
            result["WaitWhenDone"] = str(self.wait_when_done)
            
        if self.checkpoint:
            result["Checkpoint"] = "Yes"
            
        # Добавляем выводы
        if self.start_wave_output:
            result.update(self.start_wave_output.to_valve_format())
            
        if self.done_output:
            result.update(self.done_output.to_valve_format())
            
        if self.init_wave_output:
            result.update(self.init_wave_output.to_valve_format())
            
        # Добавляем кастомные выводы
        for output in self.custom_outputs:
            result.update(output.to_valve_format())
            
        # Добавляем спавны
        for spawn in self.wave_spawns:
            if "WaveSpawn" not in result:
                result["WaveSpawn"] = []
            result["WaveSpawn"].append(spawn.to_valve_format())
            
        # Добавляем танки
        for tank in self.tanks:
            if "Tank" not in result:
                result["Tank"] = []
            result["Tank"].append(tank.to_valve_format())
            
        return result

    @classmethod
    def from_valve_format(cls, data: Dict[str, Any]) -> 'Wave':
        """Создает волну из формата Valve."""
        wave = cls()
        
        # Сохраняем комментарий если он есть
        if "__comment" in data:
            wave.comment = data["__comment"]
        
        # Собираем WaveSpawn
        if "WaveSpawn" in data:
            wave_spawn_data = data["WaveSpawn"]
            if isinstance(wave_spawn_data, list):
                wave.wave_spawns.extend(WaveSpawn.from_valve_format(spawn) for spawn in wave_spawn_data)
            else:
                wave.wave_spawns.append(WaveSpawn.from_valve_format(wave_spawn_data))
                
        # Собираем Tank
        if "Tank" in data:
            tank_data = data["Tank"]
            if isinstance(tank_data, list):
                wave.tanks.extend(Tank.from_valve_format(tank) for tank in tank_data)
            else:
                wave.tanks.append(Tank.from_valve_format(tank_data))
                
        return wave

"""
Модель для представления WaveSpawn в MvM миссии.
"""
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional
from .tank import Tank
from .tf_bot import TFBot
from .base import CommentableMixin

@dataclass
class WaveSpawn(CommentableMixin):
    """Представляет WaveSpawn в MvM миссии."""
    name: str = ""
    where: str = ""
    total_count: int = 0
    max_active: int = 0
    spawn_count: int = 0
    total_currency: int = 0
    support: bool = False
    squad: List[Any] = field(default_factory=list)  # TFBot или Tank
    wait_for_all_spawned: str = ""
    wait_for_all_dead: str = ""
    wait_between_spawns: int = 0
    wait_before_starting: int = 0  # Новое поле
    random_spawn: bool = False  # Новое поле
    start_wave_output: Optional[Dict[str, Any]] = None  # Обновлено для поддержки Target/Action/Param
    first_spawn_output: Optional[Dict[str, Any]] = None
    last_spawn_output: Optional[Dict[str, Any]] = None
    done_output: Optional[Dict[str, Any]] = None
    # comment унаследован и уже идёт с дефолтом

    def to_valve_format(self) -> Dict[str, Any]:
        """Конвертирует WaveSpawn в формат Valve."""
        result = {}
        
        # Добавляем комментарий если он есть
        if self.comment:
            result["__comment"] = self.comment
        
        if self.name:
            result["Name"] = self.name
            
        if self.where:
            result["Where"] = self.where
            
        if self.total_count:
            result["TotalCount"] = self.total_count
            
        if self.max_active:
            result["MaxActive"] = self.max_active
            
        if self.spawn_count:
            result["SpawnCount"] = self.spawn_count
            
        if self.total_currency:
            result["TotalCurrency"] = self.total_currency
            
        if self.support:
            result["Support"] = 1
            
        if self.wait_for_all_spawned:
            result["WaitForAllSpawned"] = self.wait_for_all_spawned
            
        if self.wait_for_all_dead:
            result["WaitForAllDead"] = self.wait_for_all_dead
            
        if self.wait_between_spawns:
            result["WaitBetweenSpawns"] = self.wait_between_spawns
            
        if self.wait_before_starting:
            result["WaitBeforeStarting"] = self.wait_before_starting
            
        if self.random_spawn:
            result["RandomSpawn"] = 1
            
        if self.start_wave_output:
            result["StartWaveOutput"] = self.start_wave_output
            
        if self.first_spawn_output:
            result["FirstSpawnOutput"] = self.first_spawn_output
            
        if self.last_spawn_output:
            result["LastSpawnOutput"] = self.last_spawn_output
            
        if self.done_output:
            result["DoneOutput"] = self.done_output
            
        # Обрабатываем Squad
        if len(self.squad) == 1:
            bot = self.squad[0]
            if isinstance(bot, TFBot):
                result["TFBot"] = bot.to_valve_format()
            elif isinstance(bot, Tank):
                result["Tank"] = bot.to_valve_format()
        elif len(self.squad) > 1:
            result["Squad"] = {"TFBot": [bot.to_valve_format() for bot in self.squad]}
            
        return result
    
    @classmethod
    def from_valve_format(cls, data: Dict[str, Any]) -> 'WaveSpawn':
        """Создает WaveSpawn из формата Valve."""
        spawn = cls()
        
        # Сохраняем комментарий если он есть
        if "__comment" in data:
            spawn.comment = data["__comment"]
        
        if "Name" in data:
            spawn.name = data["Name"]
            
        if "Where" in data:
            spawn.where = data["Where"]
            
        if "TotalCount" in data:
            spawn.total_count = int(data["TotalCount"])
            
        if "MaxActive" in data:
            spawn.max_active = int(data["MaxActive"])
            
        if "SpawnCount" in data:
            spawn.spawn_count = int(data["SpawnCount"])
            
        if "TotalCurrency" in data:
            spawn.total_currency = int(data["TotalCurrency"])
            
        if "Support" in data:
            spawn.support = bool(int(data["Support"]))
            
        if "WaitForAllSpawned" in data:
            spawn.wait_for_all_spawned = data["WaitForAllSpawned"]
            
        if "WaitForAllDead" in data:
            spawn.wait_for_all_dead = data["WaitForAllDead"]
            
        if "WaitBetweenSpawns" in data:
            spawn.wait_between_spawns = int(data["WaitBetweenSpawns"])
            
        if "WaitBeforeStarting" in data:
            spawn.wait_before_starting = int(data["WaitBeforeStarting"])
            
        if "RandomSpawn" in data:
            spawn.random_spawn = bool(int(data["RandomSpawn"]))
            
        if "StartWaveOutput" in data:
            spawn.start_wave_output = data["StartWaveOutput"]
            
        if "FirstSpawnOutput" in data:
            spawn.first_spawn_output = data["FirstSpawnOutput"]
            
        if "LastSpawnOutput" in data:
            spawn.last_spawn_output = data["LastSpawnOutput"]
            
        if "DoneOutput" in data:
            spawn.done_output = data["DoneOutput"]
            
        # Обрабатываем Squad и TFBot
        if "Squad" in data:
            squad_data = data["Squad"]
            if isinstance(squad_data, dict) and "TFBot" in squad_data:
                bots = squad_data["TFBot"]
                if isinstance(bots, list):
                    spawn.squad.extend(TFBot.from_valve_format(bot) for bot in bots)
                else:
                    spawn.squad.append(TFBot.from_valve_format(bots))
        elif "TFBot" in data:
            spawn.squad.append(TFBot.from_valve_format(data["TFBot"]))
        elif "Tank" in data:
            spawn.squad.append(Tank.from_valve_format(data["Tank"]))
            
        return spawn

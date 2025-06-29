"""
Модель для представления спавна волны в MvM миссии.
"""
from dataclasses import dataclass, field
from typing import Dict, List, Union, Any
from .robot import Robot

@dataclass
class WaveSpawn:
    """Представляет спавн волны в MvM миссии."""
    name: str = ""
    total_count: int = 0
    max_active: int = 0
    spawn_count: int = 0
    wait_between_spawns: float = 0.0
    wait_before_starting: float = 0.0
    where: str = ""
    total_currency: int = 0
    support: bool = False
    random_spawn: bool = False
    squad: List[Union[Robot]] = field(default_factory=list)
    wait_for_all_dead: str = ""
    wait_for_all_spawned: str = ""
    
    def to_valve_format(self) -> Dict[str, Any]:
        """Конвертирует спавн в формат Valve."""
        result = {}
        
        if self.name:
            result["Name"] = self.name
            
        if self.total_count:
            result["TotalCount"] = self.total_count
            
        if self.max_active:
            result["MaxActive"] = self.max_active
            
        if self.spawn_count:
            result["SpawnCount"] = self.spawn_count
            
        if self.wait_between_spawns:
            result["WaitBetweenSpawns"] = self.wait_between_spawns
            
        if self.wait_before_starting:
            result["WaitBeforeStarting"] = self.wait_before_starting
            
        if self.where:
            result["Where"] = self.where
            
        if self.total_currency:
            result["TotalCurrency"] = self.total_currency
            
        if self.support:
            result["Support"] = 1
            
        if self.random_spawn:
            result["RandomSpawn"] = 1
            
        if self.wait_for_all_dead:
            result["WaitForAllDead"] = self.wait_for_all_dead
            
        if self.wait_for_all_spawned:
            result["WaitForAllSpawned"] = self.wait_for_all_spawned
            
        # Обработка squad
        if self.squad:
            if len(self.squad) == 1:
                # Если только один бот/танк, добавляем его напрямую
                if hasattr(self.squad[0], 'to_valve_format'):
                    if self.squad[0].__class__.__name__ == 'Tank':
                        result["Tank"] = self.squad[0].to_valve_format()
                    else:
                        result["TFBot"] = self.squad[0].to_valve_format()
            else:
                # Если больше одного, создаем Squad без Python-представления
                squad_members = []
                for member in self.squad:
                    if hasattr(member, 'to_valve_format'):
                        if member.__class__.__name__ == 'Tank':
                            squad_members.append({
                                "Tank": member.to_valve_format()
                            })
                        else:
                            squad_members.append({
                                "TFBot": member.to_valve_format()
                            })
                result["Squad"] = squad_members
                    
        return result

    @classmethod
    def from_valve_format(cls, data: Dict[str, Any]) -> 'WaveSpawn':
        """Создает спавн из формата Valve."""
        spawn = cls()
        
        if "Name" in data:
            spawn.name = data["Name"]
        if "TotalCount" in data:
            spawn.total_count = int(data["TotalCount"])
        if "MaxActive" in data:
            spawn.max_active = int(data["MaxActive"])
        if "SpawnCount" in data:
            spawn.spawn_count = int(data["SpawnCount"])
        if "WaitBetweenSpawns" in data:
            spawn.wait_between_spawns = float(data["WaitBetweenSpawns"])
        if "WaitBeforeStarting" in data:
            spawn.wait_before_starting = float(data["WaitBeforeStarting"])
        if "Where" in data:
            spawn.where = data["Where"]
        if "TotalCurrency" in data:
            spawn.total_currency = int(data["TotalCurrency"])
        if "Support" in data:
            spawn.support = bool(data["Support"])
        if "RandomSpawn" in data:
            spawn.random_spawn = bool(data["RandomSpawn"])
        if "WaitForAllDead" in data:
            spawn.wait_for_all_dead = data["WaitForAllDead"]
        if "WaitForAllSpawned" in data:
            spawn.wait_for_all_spawned = data["WaitForAllSpawned"]
            
        # Обработка squad
        if "Squad" in data:
            squad_data = data["Squad"]
            if isinstance(squad_data, list):
                for member in squad_data:
                    if "TFBot" in member:
                        spawn.squad.append(Robot.from_valve_format(member["TFBot"]))
                    elif "Tank" in member:
                        spawn.squad.append(Robot.from_valve_format(member["Tank"]))
        elif "TFBot" in data:
            spawn.squad.append(Robot.from_valve_format(data["TFBot"]))
        elif "Tank" in data:
            spawn.squad.append(Robot.from_valve_format(data["Tank"]))
            
        return spawn

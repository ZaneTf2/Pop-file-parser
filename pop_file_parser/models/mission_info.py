"""
Модель для представления корневых параметров MvM миссии.
"""
from dataclasses import dataclass, field
from typing import Dict, List, Any
from .wave import Wave
from .mission import Mission
from .base import CommentableMixin

@dataclass
class MissionInfo(CommentableMixin):
    """Представляет корневые параметры MvM миссии."""
    starting_currency: int = 400
    robot_limit: int = 22
    allow_bot_extra_slots: bool = False
    respawn_wave_time: int = 6
    fixed_respawn_wave_time: bool = False
    can_bots_attack_in_spawn: bool = True
    waves: List[Wave] = field(default_factory=list)
    missions: List[Mission] = field(default_factory=list)
    
    def to_valve_format(self) -> Dict[str, Any]:
        """Конвертирует параметры миссии в формат Valve."""
        result = {}
        
        # Добавляем комментарий если он есть
        if self.comment:
            result["__comment"] = self.comment
            
        if self.starting_currency != 400:
            result["StartingCurrency"] = self.starting_currency
            
        if self.robot_limit != 22:
            result["RobotLimit"] = self.robot_limit
            
        if self.allow_bot_extra_slots:
            result["AllowBotExtraSlots"] = 1
            
        if self.respawn_wave_time != 6:
            result["RespawnWaveTime"] = self.respawn_wave_time
            
        if self.fixed_respawn_wave_time:
            result["FixedRespawnWaveTime"] = "Yes"
            
        if not self.can_bots_attack_in_spawn:
            result["CanBotsAttackWhileInSpawnRoom"] = "no"
            
        if self.waves:
            result["Wave"] = [wave.to_valve_format() for wave in self.waves]
            
        if self.missions:
            result["Mission"] = [mission.to_valve_format() for mission in self.missions]
            
        return result
        
    @classmethod
    def from_valve_format(cls, data: Dict[str, Any]) -> 'MissionInfo':
        """Создает параметры миссии из формата Valve."""
        info = cls()
        
        # Сохраняем комментарий если он есть
        if "__comment" in data:
            info.comment = data["__comment"]
            
        if "StartingCurrency" in data:
            info.starting_currency = int(data["StartingCurrency"])
            
        if "RobotLimit" in data:
            info.robot_limit = int(data["RobotLimit"])
            
        if "AllowBotExtraSlots" in data:
            info.allow_bot_extra_slots = bool(data["AllowBotExtraSlots"])
            
        if "RespawnWaveTime" in data:
            info.respawn_wave_time = int(data["RespawnWaveTime"])
            
        if "FixedRespawnWaveTime" in data:
            info.fixed_respawn_wave_time = data["FixedRespawnWaveTime"].lower() == "yes"
            
        if "CanBotsAttackWhileInSpawnRoom" in data:
            info.can_bots_attack_in_spawn = data["CanBotsAttackWhileInSpawnRoom"].lower() != "no"
            
        if "Wave" in data:
            info.waves = [Wave.from_valve_format(wave) for wave in data["Wave"]]
            
        if "Mission" in data:
            info.missions = [Mission.from_valve_format(mission) for mission in data["Mission"]]
            
        return info

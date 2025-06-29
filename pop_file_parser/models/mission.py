"""
Модель для представления миссии поддержки в MvM.
"""
from dataclasses import dataclass
from typing import Dict, Any, Optional
from .robot import Robot
from .base import CommentableMixin

@dataclass
class Mission(CommentableMixin):
    """Представляет миссию поддержки в MvM (Spy, Sniper, Engineer, Sentry Buster)."""
    objective: str = ""
    initial_cooldown: int = 0
    where: str = ""
    begin_at_wave: int = 0
    run_for_waves: int = 0
    cooldown_time: int = 0
    tf_bot: Optional[Robot] = None
    desired_count: Optional[int] = None
    max_active: Optional[int] = None
    # comment унаследован от CommentableMixin

    def to_valve_format(self) -> Dict[str, Any]:
        """Конвертирует миссию в формат Valve."""
        result = {}
        
        # Добавляем комментарий если он есть
        if self.comment:
            result["__comment"] = self.comment
            
        if self.objective:
            result["Objective"] = self.objective
            
        if self.initial_cooldown:
            result["InitialCooldown"] = self.initial_cooldown
            
        if self.where:
            result["Where"] = self.where
            
        if self.begin_at_wave:
            result["BeginAtWave"] = self.begin_at_wave
            
        if self.run_for_waves:
            result["RunForThisManyWaves"] = self.run_for_waves
            
        if self.cooldown_time:
            result["CooldownTime"] = self.cooldown_time
            
        if self.desired_count:
            result["DesiredCount"] = self.desired_count
            
        if self.max_active:
            result["MaxActive"] = self.max_active
            
        if self.tf_bot:
            result["TFBot"] = self.tf_bot.to_valve_format()
            
        return result
        
    @classmethod
    def from_valve_format(cls, data: Dict[str, Any]) -> 'Mission':
        """Создает Mission из формата Valve."""
        mission = cls()
        
        # Сохраняем комментарий если он есть
        if "__comment" in data:
            mission.comment = data["__comment"]
            
        if "Objective" in data:
            mission.objective = data["Objective"]
            
        if "InitialCooldown" in data:
            mission.initial_cooldown = data["InitialCooldown"]
            
        if "Where" in data:
            mission.where = data["Where"]
            
        if "BeginAtWave" in data:
            mission.begin_at_wave = data["BeginAtWave"]
            
        if "RunForThisManyWaves" in data:
            mission.run_for_waves = data["RunForThisManyWaves"]
            
        if "CooldownTime" in data:
            mission.cooldown_time = data["CooldownTime"]
            
        if "DesiredCount" in data:
            mission.desired_count = data["DesiredCount"]
            
        if "MaxActive" in data:
            mission.max_active = data["MaxActive"]
            
        if "TFBot" in data:
            mission.tf_bot = Robot.from_valve_format(data["TFBot"])
            
        return mission

        return result

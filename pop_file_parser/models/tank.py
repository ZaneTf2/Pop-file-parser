"""
Модель для представления Tank в MvM миссии.
"""
from dataclasses import dataclass
from typing import Dict, Any
from .base import CommentableMixin

@dataclass
class Tank(CommentableMixin):
    """Представляет Tank в MvM миссии."""
    name: str = "tankboss"
    health: int = 0
    speed: int = 75
    skin: int = 0
    start_disabled: bool = False
    # comment унаследован и уже идёт с дефолтом

    def to_valve_format(self) -> Dict[str, Any]:
        """Конвертирует Tank в формат Valve."""
        result = {}
        
        # Добавляем комментарий если он есть
        if self.comment:
            result["__comment"] = self.comment
            
        if self.name:
            result["Name"] = self.name
            
        if self.health:
            result["Health"] = self.health
            
        if self.speed != 75:  # Значение по умолчанию
            result["Speed"] = self.speed
            
        if self.skin:
            result["Skin"] = self.skin
            
        if self.start_disabled:
            result["StartDisabled"] = 1
            
        return result
    
    @classmethod
    def from_valve_format(cls, data: Dict[str, Any]) -> 'Tank':
        """Создает Tank из формата Valve."""
        tank = cls()
        
        # Сохраняем комментарий если он есть
        if "__comment" in data:
            tank.comment = data["__comment"]
        
        if "Name" in data:
            tank.name = data["Name"]
            
        if "Health" in data:
            tank.health = int(data["Health"])
            
        if "Speed" in data:
            tank.speed = int(data["Speed"])
            
        if "Skin" in data:
            tank.skin = int(data["Skin"])
            
        if "StartDisabled" in data:
            tank.start_disabled = bool(int(data["StartDisabled"]))
            
        return tank

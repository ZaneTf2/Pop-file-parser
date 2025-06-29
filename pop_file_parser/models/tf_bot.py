"""
Модель для представления TFBot в MvM миссии.
"""
from dataclasses import dataclass, field
from typing import Dict, List, Set, Any
from .base import CommentableMixin

@dataclass
class TFBot(CommentableMixin):
    """Представляет TFBot в MvM миссии."""
    name: str = ""
    class_name: str = ""
    health: int = 0
    skill: str = "Normal"
    scale: float = 1.0
    template: str = ""
    attributes: Set[str] = field(default_factory=set)
    items: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    item_attributes: Dict[str, Any] = field(default_factory=dict)
    character_attributes: Dict[str, Any] = field(default_factory=dict)
    weapons: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    class_icon: str = ""  # Новое поле
    max_vision_range: int = 0  # Новое поле
    weapon_restrictions: str = ""  # Новое поле
    action: str = ""  # Новое поле
    teleport_where: str = ""  # Новое поле
    use_custom_model: str = ""  # Новое поле
    
    # comment унаследован и уже идёт с дефолтом

    def to_valve_format(self) -> Dict[str, Any]:
        """Конвертирует TFBot в формат Valve."""
        result = {}
        
        # Добавляем комментарий если он есть
        if self.comment:
            result["__comment"] = self.comment
            
        if self.template:
            result["Template"] = self.template
            return result
            
        if self.name:
            result["Name"] = self.name
            
        if self.class_name:
            result["Class"] = self.class_name
            
        if self.health:
            result["Health"] = self.health
            
        if self.skill:
            result["Skill"] = self.skill
            
        if self.scale != 1.0:
            result["Scale"] = self.scale
            
        if self.class_icon:
            result["ClassIcon"] = self.class_icon
            
        if self.max_vision_range:
            result["MaxVisionRange"] = self.max_vision_range
            
        if self.weapon_restrictions:
            result["WeaponRestrictions"] = self.weapon_restrictions
            
        if self.action:
            result["Action"] = self.action
            
        if self.teleport_where:
            result["TeleportWhere"] = self.teleport_where
            
        if self.use_custom_model:
            result["UseCustomModel"] = self.use_custom_model
            
        if self.attributes:
            result["__attrs"] = list(self.attributes)
            
        if self.items:
            for item in self.items:
                result.setdefault("Item", []).append(item)
                
        if self.tags:
            result["Tags"] = self.tags
            
        if self.item_attributes:
            result["ItemAttributes"] = self.item_attributes
            
        if self.character_attributes:
            result["CharacterAttributes"] = self.character_attributes
            
        if self.weapons:
            for weapon_name, weapon_attrs in self.weapons.items():
                weapon_data = {"name": weapon_name}
                weapon_data.update(weapon_attrs)
                result.setdefault("WeaponRestrictions", []).append(weapon_data)
                
        return result
    
    @classmethod
    def from_valve_format(cls, data: Dict[str, Any]) -> 'TFBot':
        """Создает TFBot из формата Valve."""
        bot = cls()
        
        # Сохраняем комментарий если он есть
        if "__comment" in data:
            bot.comment = data["__comment"]
            
        if "Template" in data:
            bot.template = data["Template"]
            return bot
            
        if "Name" in data:
            bot.name = data["Name"]
            
        if "Class" in data:
            bot.class_name = data["Class"]
            
        if "Health" in data:
            bot.health = data["Health"]
            
        if "Skill" in data:
            bot.skill = data["Skill"]
            
        if "Scale" in data:
            bot.scale = float(data["Scale"])
            
        if "Item" in data:
            items = data["Item"]
            if isinstance(items, list):
                bot.items.extend(items)
            else:
                bot.items.append(items)
                
        if "Attributes" in data:
            attrs = data["Attributes"]
            if isinstance(attrs, list):
                bot.attributes.update(attrs)
            else:
                bot.attributes.add(attrs)
                
        if "Tags" in data:
            bot.tags = data["Tags"]
            
        if "ItemAttributes" in data:
            bot.item_attributes = data["ItemAttributes"]
            
        if "CharacterAttributes" in data:
            bot.character_attributes = data["CharacterAttributes"]
            
        if "WeaponRestrictions" in data:
            for weapon in data["WeaponRestrictions"]:
                if isinstance(weapon, dict) and "name" in weapon:
                    name = weapon.pop("name")
                    bot.weapons[name] = weapon
                    
        return bot

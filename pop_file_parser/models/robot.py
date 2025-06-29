"""
Модель для представления робота в MvM миссии.
"""
import logging
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any

logger = logging.getLogger(__name__)

@dataclass
class Robot:
    """Представляет робота в MvM миссии."""
    name: str
    class_name: Optional[str] = None
    health: Optional[int] = None
    skill: Optional[str] = None
    scale: float = 1.0
    items: List[str] = field(default_factory=list)
    attributes: Dict[str, Any] = field(default_factory=dict)
    character_attributes: Dict[str, Any] = field(default_factory=dict)
    weapon_restrictions: Optional[str] = None

    def to_valve_format(self) -> Dict[str, Any]:
        """Конвертирует робота в формат Valve."""
        result: Dict[str, Any] = {}

        # Проверяем наличие шаблона
        if "Template" in self.attributes:
            result["Template"] = self.attributes["Template"]
            # Добавляем имя только если оно явно указано
            if "Name" in self.attributes:
                result["Name"] = self.attributes["Name"]
        else:
            # Если нет шаблона - добавляем все базовые атрибуты
            result["Name"] = self.name

            if self.class_name:
                result["Class"] = self.class_name

            if self.health:
                result["Health"] = self.health

            if self.skill:
                result["Skill"] = self.skill

            if self.scale != 1.0:
                result["Scale"] = str(self.scale)

        # Каждый Item на отдельной строке
        for item in self.items:
            if "Item" not in result:
                result["Item"] = item
            else:
                if isinstance(result["Item"], list):
                    result["Item"].append(item)
                else:
                    result["Item"] = [result["Item"], item]

        if self.weapon_restrictions:
            result["WeaponRestrictions"] = self.weapon_restrictions

        # Каждый Attribute на отдельной строке
        if "Attributes" in self.attributes:
            attrs = self.attributes["Attributes"]
            if isinstance(attrs, str):
                result["Attributes"] = attrs
            elif isinstance(attrs, list):
                result["Attributes"] = attrs

        if self.character_attributes:
            result["CharacterAttributes"] = self.character_attributes.copy()

        # Обрабатываем атрибуты предметов
        if "ItemAttributes" in self.attributes:
            item_attrs = self.attributes["ItemAttributes"]

            if isinstance(item_attrs, dict):
                # Один блок ItemAttributes
                if "ItemName" in item_attrs:
                    item_name = item_attrs["ItemName"]
                    if item_name not in self.items:
                        logger.warning(f"ItemName '{item_name}' указан в ItemAttributes, но предмет не найден в списке предметов робота '{self.name}'. ItemAttributes будет пропущен.")
                    else:
                        result["ItemAttributes"] = item_attrs
                else:
                    # Если ItemName не указан - используем последний предмет
                    if self.items:
                        attrs_copy = item_attrs.copy()
                        attrs_copy["ItemName"] = self.items[-1]
                        logger.warning(f"ItemName не указан в ItemAttributes для робота '{self.name}', используем последний предмет '{self.items[-1]}'")
                        result["ItemAttributes"] = attrs_copy
                    else:
                        logger.warning(f"ItemAttributes указан для робота '{self.name}', но нет ни одного предмета. ItemAttributes будет пропущен.")

            elif isinstance(item_attrs, list):
                # Список блоков ItemAttributes
                result["ItemAttributes"] = []
                for attrs in item_attrs:
                    if isinstance(attrs, dict):
                        if "ItemName" in attrs:
                            item_name = attrs["ItemName"]
                            if item_name not in self.items:
                                logger.warning(f"ItemName '{item_name}' указан в ItemAttributes, но предмет не найден в списке предметов робота '{self.name}'. Блок будет пропущен.")
                            else:
                                result["ItemAttributes"].append(attrs)
                        else:
                            logger.warning(f"Блок ItemAttributes без ItemName для робота '{self.name}' будет пропущен.")

                # Если все блоки были пропущены - удаляем пустой список
                if not result["ItemAttributes"]:
                    del result["ItemAttributes"]

        # Добавляем остальные атрибуты кроме уже обработанных
        for key, value in self.attributes.items():
            if key not in ["ItemAttributes", "Attributes", "Template", "Name"]:
                result[key] = value

        return result

    @classmethod
    def from_valve_format(cls, data: Dict[str, Any]) -> 'Robot':
        """Создает робота из формата Valve."""
        name = data.get("Name", "Unknown")
        items = []
        
        # Собираем все Item в список
        if "Item" in data:
            if isinstance(data["Item"], list):
                items.extend(data["Item"])
            else:
                items.append(data["Item"])
                
        character_attributes = {}
        if "CharacterAttributes" in data:
            character_attributes = data["CharacterAttributes"]
            
        # Копируем все остальные атрибуты
        attributes = data.copy()
        for key in ["Name", "Class", "Health", "Skill", "Scale", "Item", 
                   "CharacterAttributes", "WeaponRestrictions"]:
            attributes.pop(key, None)
            
        return cls(
            name=name,
            class_name=data.get("Class"),
            health=int(data["Health"]) if "Health" in data else None,
            skill=data.get("Skill"),
            scale=float(data.get("Scale", 1.0)),
            items=items,
            character_attributes=character_attributes,
            attributes=attributes,
            weapon_restrictions=data.get("WeaponRestrictions")
        )

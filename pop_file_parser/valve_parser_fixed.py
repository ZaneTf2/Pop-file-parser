"""
Парсер для формата файлов Valve (используется в Source engine).
"""
from typing import Any, Dict

class ValveFormat:
    """Парсер формата Valve."""
    
    def __init__(self):
        self.text = ""
        self.pos = 0
        self.line = 1
        self.column = 1
        self.comments = {}  # Хранение комментариев для блоков
        
    # ... (предыдущие методы остаются без изменений)
    
    def _is_root_param(self, key: str) -> bool:
        """Проверяет, является ли параметр корневым."""
        root_params = {
            "FixedRespawnWaveTime", "CanBotsAttackWhileInSpawnRoom", 
            "AddSentryBusterWhenDamageDealtExceeds", "Advanced"
        }
        return key in root_params

    def _format_boolean(self, key: str, value: bool) -> str:
        """Форматирует булево значение."""
        if self._is_root_param(key):
            return f'{key} {"Yes" if value else "No"}'
        return f'{key} {1 if value else 0}'

    def _format_key_value(self, key: str, value: Any, indent: int = 0) -> str:
        """Форматирует пару ключ-значение."""
        # Специальный ключ для атрибутов
        if key == "__attrs":
            return f'Attributes {" ".join(value)}'

        # Имена блоков без кавычек
        if isinstance(value, (dict, list)) and key in {
            "WaveSchedule", "Wave", "WaveSpawn", "Tank", "TFBot", 
            "Mission", "CharacterAttributes", "ItemAttributes", "Squad"
        }:
            return key

        # Булевы значения
        if isinstance(value, bool):
            return self._format_boolean(key, value)

        # Числовые значения без кавычек
        if isinstance(value, (int, float)):
            # ItemName всегда в кавычках
            if key == "ItemName":
                return f'{key} "{value}"'
            return f'{key} {value}'

        # Where и подобные всегда в кавычках
        if key in {"Where", "Name", "Template", "ItemName"}:
            return f'{key} "{value}"'

        # Обычные строки в кавычках если содержат пробелы
        if isinstance(value, str) and (" " in value or not value.isalnum()):
            return f'{key} "{value}"'
            
        return f'{key} {value}'

    def dump(self, data: Dict[str, Any], indent: int = 0) -> str:
        """Форматирует данные в формат Valve."""
        result = []
        special_keys = {"__comment", "__base_files", "__attrs"}
        regular_data = {k: v for k, v in data.items() if k not in special_keys}
        
        # Сначала обрабатываем атрибуты, если они есть
        if "__attrs" in data:
            result.append("\t" * indent + f'Attributes {" ".join(data["__attrs"])}')
            
        for key, value in regular_data.items():
            if isinstance(value, dict):
                if key == "Attributes":
                    # Специальная обработка для Attributes
                    attrs = []
                    for attr_key, attr_val in value.items():
                        if attr_key:  # Пропускаем пустые ключи
                            attrs.append(attr_val)
                    if attrs:
                        result.append("\t" * indent + f'Attributes {" ".join(attrs)}')
                elif key in {"CharacterAttributes", "ItemAttributes"}:
                    # Специальная обработка для CharacterAttributes и ItemAttributes
                    result.append("\t" * indent + key)
                    result.append("\t" * indent + "{")
                    for attr_key, attr_val in value.items():
                        if attr_key == "ItemName":
                            result.append("\t" * (indent + 1) + f'ItemName "{attr_val}"')
                        elif isinstance(attr_val, (int, float)):
                            result.append("\t" * (indent + 1) + f'"{attr_key}" {attr_val}')
                        else:
                            result.append("\t" * (indent + 1) + f'"{attr_key}" "{attr_val}"')
                    result.append("\t" * indent + "}")
                else:
                    # Обычный блок
                    result.append("\t" * indent + self._format_key_value(key, value))
                    result.append("\t" * indent + "{")
                    result.append(self.dump(value, indent + 1))
                    result.append("\t" * indent + "}")
            elif isinstance(value, list):
                if key == "Squad":
                    # Специальная обработка для Squad
                    result.append("\t" * indent + key)
                    result.append("\t" * indent + "{")
                    for member in value:
                        member_type = next(iter(member))  # TFBot или Tank
                        result.append("\t" * indent + member_type)
                        result.append("\t" * indent + "{")
                        result.append(self.dump(member[member_type], indent + 1))
                        result.append("\t" * indent + "}")
                    result.append("\t" * indent + "}")
                else:
                    # Для других списков (например, Wave) - каждый элемент как отдельный блок
                    for item in value:
                        if isinstance(item, dict):
                            result.append("\t" * indent + self._format_key_value(key, item))
                            result.append("\t" * indent + "{")
                            result.append(self.dump(item, indent + 1))
                            result.append("\t" * indent + "}")
                        else:
                            result.append("\t" * indent + self._format_key_value(key, item))
            else:
                result.append("\t" * indent + self._format_key_value(key, value))
        
        return "\n".join(result)

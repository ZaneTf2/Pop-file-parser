"""
Модель для представления output блоков в MvM.
"""
from dataclasses import dataclass
from typing import Dict, Any
from .base import CommentableMixin


@dataclass
class OutputBlock(CommentableMixin):
    """
    Представляет output блок в MvM (StartWaveOutput, DoneOutput, InitWaveOutput и др.).
    
    Attributes:
        name: Имя блока (StartWaveOutput, DoneOutput и т.д.)
        target: Цель (relay или другой entity)
        action: Действие (Trigger, Kill и т.д.)
        custom_settings: Дополнительные настройки в формате Valve. Для Parameters может быть словарем.
    """
    name: str = ""
    target: str = ""
    action: str = ""
    custom_settings: Any = ""  # Может быть str или dict для Parameters
    # comment унаследован и уже идёт с дефолтом

    def to_valve_format(self) -> Dict[str, Any]:
        """Конвертирует output блок в формат Valve."""
        if self.name == "Parameters":
            # Для блока Parameters
            if isinstance(self.custom_settings, dict):
                # Если custom_settings уже словарь, используем его напрямую
                parameters = self.custom_settings
            elif isinstance(self.custom_settings, str):
                # Если custom_settings строка, сначала проверяем не Python-словарь ли это
                if self.custom_settings.strip().startswith("{'") and self.custom_settings.strip().endswith("'}"):
                    # Это Python-словарь, извлекаем значения
                    try:
                        import ast
                        # Безопасно парсим строку словаря
                        parameters = ast.literal_eval(self.custom_settings)
                    except:
                        parameters = {}
                else:
                    # Если это не Python-словарь или парсинг не удался,
                    # обрабатываем как обычную строку в формате Valve
                    settings_str = self.custom_settings.strip().strip('{}')
                    parameters = {}
                    
                    for line in settings_str.strip().split('\n'):
                        line = line.strip()
                        if not line:
                            continue
                        
                        parts = line.split(maxsplit=1)
                        if len(parts) == 1:
                            parameters[parts[0]] = ""
                        else:
                            key, value = parts
                            # Убираем кавычки, если они есть
                            if value.startswith('"') and value.endswith('"'):
                                value = value[1:-1]
                            parameters[key] = value
            else:
                parameters = {}
                
            result = {"Parameters": parameters}
            # Добавляем комментарий если он есть
            if self.comment:
                result["__comment"] = self.comment
            return result
        else:
            # Для обычных output блоков
            output_data = {}
            if self.target:
                output_data["Target"] = self.target
            if self.action:
                output_data["Action"] = self.action
                
            result = {self.name: output_data}
            # Добавляем комментарий если он есть
            if self.comment:
                result["__comment"] = self.comment
            return result

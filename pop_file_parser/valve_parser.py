"""
Парсер для формата файлов Valve (используется в Source engine).
"""
from typing import Any, Dict, List, Union
import re

class ValveFormat:
    """Парсер формата Valve."""
    
    def __init__(self):
        self.text = ""
        self.pos = 0
        self.line = 1
        self.column = 1
        self.comments = {}  # Хранение комментариев для блоков
        
    def parse_file(self, file_path: str) -> Dict[str, Any]:
        """Парсит файл формата Valve."""
        with open(file_path, 'r', encoding='utf-8') as f:
            self.text = f.read()
            
        # Сохраняем комментарии перед блоками
        self._extract_block_comments()
        
        # Удаляем однострочные комментарии
        self.text = re.sub(r'//.*?\n', '\n', self.text)
        # Удаляем многострочные комментарии
        self.text = re.sub(r'/\*.*?\*/', '', self.text, flags=re.DOTALL)
        
        # Обрабатываем директивы #base
        base_files = []
        for match in re.finditer(r'#base\s+"?([^"\n]+)"?', self.text):
            base_files.append(match.group(1))
            
        # Удаляем директивы #base из текста
        self.text = re.sub(r'#base\s+"?[^"\n]+"?\s*\n', '', self.text)
            
        self.pos = 0
        self.line = 1
        self.column = 1

        self._skip_whitespace()
        if self.pos < len(self.text) and self.text[self.pos] != '{':
            root_key = self._parse_string()
            self._skip_whitespace()
            if self.pos < len(self.text) and self.text[self.pos] == '{':
                result = {root_key: self._parse_block()}
            else:
                raise ValueError(f"Expected '{{' after root key at line {self.line}, column {self.column}")
        else:
            result = self._parse_block()
        
        # Добавляем комментарии к блокам
        self._add_comments_to_result(result)
        
        # Добавляем информацию о базовых файлах
        if base_files:
            result["__base_files"] = base_files
            
        return result
    
    def _extract_block_comments(self):
        """Извлекает комментарии перед блоками."""
        # Ищем комментарии перед каждым блоком
        block_pattern = re.compile(r'(?:/\*(?P<multi>.*?)\*/\s*|\s*(?P<single>//[^\n]*\n)+\s*)(?P<key>[A-Za-z][A-Za-z0-9_]*)\s*{', re.DOTALL)
        
        for match in block_pattern.finditer(self.text):
            comment = match.group('multi') or match.group('single')
            key = match.group('key')
            if comment:
                # Очищаем комментарий от /*, */, // и лишних пробелов
                comment = re.sub(r'/\*|\*/|//|\n\s*', ' ', comment).strip()
                self.comments[key] = comment

    def _skip_whitespace(self):
        """Пропускает пробельные символы."""
        while (
            self.pos < len(self.text) and 
            self.text[self.pos].isspace()
        ):
            if self.text[self.pos] == '\n':
                self.line += 1
                self.column = 1
            else:
                self.column += 1
            self.pos += 1
            
    def _parse_string(self) -> str:
        """Парсит строковое значение."""
        start = self.pos
        if self.text[self.pos] == '"':
            # Строка в кавычках
            self.pos += 1
            start = self.pos
            while self.pos < len(self.text) and self.text[self.pos] != '"':
                if self.text[self.pos] == '\n':
                    self.line += 1
                    self.column = 1
                else:
                    self.column += 1
                self.pos += 1
            end = self.pos
            self.pos += 1
            return self.text[start:end]
        else:
            # Строка без кавычек
            while (
                self.pos < len(self.text) and 
                not self.text[self.pos].isspace() and 
                self.text[self.pos] not in '{}'
            ):
                self.column += 1
                self.pos += 1
            return self.text[start:self.pos]
            
    def _parse_value(self) -> Union[str, Dict[str, Any], List[Any]]:
        """Парсит значение (строку или блок)."""
        self._skip_whitespace()
        
        if self.pos >= len(self.text):
            raise ValueError(f"Unexpected end of file at line {self.line}, column {self.column}")
            
        if self.text[self.pos] == '{':
            return self._parse_block()
        else:
            return self._parse_string()
            
    def _parse_block(self) -> Dict[str, Any]:
        """Парсит блок в фигурных скобках."""
        self._skip_whitespace()
        
        if self.pos >= len(self.text) or self.text[self.pos] != '{':
            raise ValueError(
                f"Expected '{{' at line {self.line}, column {self.column}"
            )
            
        self.pos += 1
        self.column += 1
        
        result = {}
        current_key = None
        current_array = []
        
        while self.pos < len(self.text):
            self._skip_whitespace()
            
            if self.text[self.pos] == '}':
                self.pos += 1
                self.column += 1
                # Если был массив, сохраняем его
                if current_key and current_array:
                    result[current_key] = current_array
                return result
                
            # Парсим ключ
            if not current_key:
                current_key = self._parse_string()
                continue
                
            # Парсим значение
            value = self._parse_value()
            
            # Если это не первое значение для этого ключа,
            # преобразуем в массив
            if current_key in result:
                if isinstance(result[current_key], list):
                    result[current_key].append(value)
                else:
                    result[current_key] = [result[current_key], value]
            else:
                result[current_key] = value
                
            current_key = None
            
        raise ValueError(
            f"Expected '}}' at line {self.line}, column {self.column}"
        )
    
    def _add_comments_to_result(self, result: Dict[str, Any], prefix: str = ""):
        """Добавляет сохраненные комментарии к блокам в результат."""
        if isinstance(result, dict):
            # Если в блоке уже есть __comment, не перезаписываем его
            for key, value in result.items():
                full_key = f"{prefix}{key}" if prefix else key
                if full_key in self.comments and "__comment" not in value:
                    if isinstance(value, dict):
                        value["__comment"] = self.comments[full_key]
                    else:
                        # Если значение не словарь, создаем словарь с комментарием
                        result[key] = {
                            "__comment": self.comments[full_key],
                            "value": value
                        }
                # Рекурсивно обрабатываем вложенные блоки
                if isinstance(value, dict):
                    self._add_comments_to_result(value, f"{full_key}.")

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

        # Обычные строки в кавычках
        return f'{key} "{value}"'

    def _is_output_block(self, key: str) -> bool:
        """Проверяет, является ли ключ Output блоком."""
        return any(key.endswith(suffix) for suffix in [
            "Output", "WaveOutput", "SpawnOutput", "DeathOutput",
            "BombDroppedOutput", "KilledOutput"
        ])

    def _format_parameters(self, value: Dict[str, Any], indent: int) -> List[str]:
        """Форматирует блок Parameters."""
        result = []
        result.append("\t" * indent + "Parameters")
        result.append("\t" * indent + "{")
        for key, val in value.items():
            result.append("\t" * (indent + 1) + f"{key} {val}")
        result.append("\t" * indent + "}")
        return result

    def _format_block(self, data: Union[Dict[str, Any], List[Dict[str, Any]]], indent: int = 0) -> List[str]:
        """Форматирует блок данных."""
        result = []

        if isinstance(data, list):
            # Форматируем список блоков
            for item in data:
                result.extend(self._format_block(item, indent))
            return result

        regular_data = {}
        list_data = {}

        # Разделяем данные на обычные и списки
        for key, value in data.items():
            if isinstance(value, list) and value and isinstance(value[0], dict):
                list_data[key] = value
            else:
                regular_data[key] = value

        # Обрабатываем обычные данные
        for key, value in regular_data.items():
            if isinstance(value, dict):
                if self._is_output_block(key) or key == "Parameters":
                    # Специальная обработка для Output блоков и Parameters
                    result.extend(self._format_output_block(key, value, indent))
                    continue
                elif key == "Attributes":
                    # Пропускаем Attributes, так как они уже были обработаны через __attrs
                    continue
                
                # Обычный блок
                result.append(" " * indent + key)
                result.append(" " * indent + "{")
                result.extend(self._format_block(value, indent + 4))
                result.append(" " * indent + "}")
            else:
                # Простое значение
                formatted_value = self._format_value(value)
                result.append(f"{' ' * indent}{key} {formatted_value}")

        # Обрабатываем списки
        for key, value in list_data.items():
            for item in value:
                result.append(" " * indent + key)
                result.append(" " * indent + "{")
                result.extend(self._format_block(item, indent + 4))
                result.append(" " * indent + "}")

        return result

    def _format_output_block(self, key: str, value: Dict[str, Any], indent: int) -> List[str]:
        """Форматирует Output блок или Parameters."""
        result = []
        result.append("\t" * indent + key)
        result.append("\t" * indent + "{")
        
        if key == "Parameters":
            # Специальная обработка Parameters - только как блок, без строкового значения
            for param_key, param_value in value.items():
                formatted_value = self._format_value(param_value)
                # Используем табуляцию для отступов
                result.append(f"\t" * (indent + 1) + f"{param_key} {formatted_value}")
        else:
            # Обычный Output блок
            for output_key, output_value in value.items():
                # Используем табуляцию для отступов
                result.append(f"\t" * (indent + 1) + f"{output_key} {self._format_value(output_value)}")
            
        result.append("\t" * indent + "}")
        return result

    def dump(self, data: Dict[str, Any], indent: int = 0) -> str:
        """Форматирует данные в формат Valve."""
        result = []
        special_keys = {"__comment", "__base_files", "__attrs"}
        
        # Если есть комментарий, добавляем его первым
        if "__comment" in data:
            comment = data["__comment"]
            # Разбиваем комментарий на строки и форматируем каждую как однострочный комментарий
            for line in comment.split('\n'):
                result.append("\t" * indent + f"// {line.strip()}")
        
        regular_data = {k: v for k, v in data.items() if k not in special_keys}
        
        # Сначала обрабатываем атрибуты, если они есть
        if "__attrs" in data:
            for attr in data["__attrs"]:
                result.append("\t" * indent + f'Attributes {attr}')
            
        for key, value in regular_data.items():
            if isinstance(value, dict):
                if self._is_output_block(key):
                    # Специальная обработка для Output блоков
                    result.extend(self._format_output_block(key, value, indent))
                elif key == "Parameters":
                    # Специальная обработка для Parameters - только как блок, без строкового значения
                    result.extend(self._format_output_block(key, value, indent))
                elif key == "Attributes":
                    # Специальная обработка для Attributes
                    if isinstance(value, (str, list)):
                        # Если это строка или список, выводим как есть
                        attrs = value if isinstance(value, list) else [value]
                        for attr in attrs:
                            result.append("\t" * indent + f'Attributes {attr}')
                    else:
                        # Если это словарь или что-то другое, извлекаем значения
                        for attr_val in value.values():
                            if attr_val:  # Пропускаем пустые значения
                                result.append("\t" * indent + f'Attributes {attr_val}')
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
            elif isinstance(value, (list, tuple)):
                # Для списков проверяем, не Squad ли это
                if key == "Squad":
                    result.append("\t" * indent + "Squad")
                    result.append("\t" * indent + "{")
                    for item in value:
                        if isinstance(item, dict):
                            item_type = next(iter(item))  # TFBot или Tank
                            result.append("\t" * (indent + 1) + item_type)
                            result.append("\t" * (indent + 1) + "{")
                            result.append(self.dump(item[item_type], indent + 2))
                            result.append("\t" * (indent + 1) + "}")
                        else:
                            # Если элемент не словарь, форматируем его как есть
                            result.append("\t" * (indent + 1) + str(item))
                    result.append("\t" * indent + "}")
                else:
                    # Для обычных списков - каждый элемент как отдельный блок
                    for item in value:
                        if isinstance(item, dict):
                            result.append("\t" * indent + self._format_key_value(key, item))
                            result.append("\t" * indent + "{")
                            result.append(self.dump(item, indent + 1))
                            result.append("\t" * indent + "}")
                        else:
                            result.append("\t" * indent + self._format_key_value(key, item))
            else:
                # Простые значения (строки, числа, булевы)
                # Пропускаем вывод Parameters как строки
                if key != "Parameters":
                    result.append("\t" * indent + self._format_key_value(key, value))
        
        return "\n".join(result)

    def _format_value(self, value: Any) -> str:
        """Форматирует отдельное значение для Valve-формата."""
        if isinstance(value, bool):
            return "Yes" if value else "No"
        if isinstance(value, (int, float)):
            return str(value)
        if value is None:
            return ''
        return f'"{value}"'

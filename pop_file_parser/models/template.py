"""
Модель для представления шаблонов роботов в MvM.
"""
from dataclasses import dataclass, field
from typing import Dict, Optional, Any
from .tf_bot import TFBot

@dataclass
class Template:
    """Представляет шаблон робота в MvM."""
    name: str
    bot: TFBot
    comments: str = ""

    def add_comments(self, comments: str) -> None:
        """Добавляет комментарии к шаблону."""
        self.comments = comments

    def to_valve_format(self) -> Dict[str, Any]:
        """Конвертирует шаблон в формат Valve."""
        result = {
            self.name: self.bot.to_valve_format()
        }
        if self.comments:
            result["__comment"] = self.comments
        return result

class TemplateManager:
    """Менеджер шаблонов для MvM."""
    
    def __init__(self):
        self.templates: Dict[str, Template] = {}
        
    def add_template(self, name: str, bot: TFBot, comments: str = "") -> None:
        """
        Добавляет новый шаблон.
        
        Args:
            name: Имя шаблона
            bot: Объект TFBot
            comments: Комментарии к шаблону
        """
        template = Template(name=name, bot=bot, comments=comments)
        self.templates[name] = template
        
    def get_template(self, name: str) -> Optional[Template]:
        """
        Получает шаблон по имени.
        
        Args:
            name: Имя шаблона
        """
        return self.templates.get(name)
        
    def to_valve_format(self) -> Dict[str, Any]:
        """Конвертирует все шаблоны в формат Valve."""
        result = {}
        for template in self.templates.values():
            result.update(template.to_valve_format())
        return result

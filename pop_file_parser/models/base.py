"""
Базовые классы и миксины для моделей.
"""
from dataclasses import dataclass, field

@dataclass
class CommentableMixin:
    """Миксин для добавления поддержки комментариев."""
    comment: str = field(default="")
    
    def add_comment(self, comment: str) -> None:
        """Добавляет комментарий к объекту."""
        self.comment = comment
        
    def get_comment(self) -> str:
        """Возвращает комментарий объекта."""
        return self.comment

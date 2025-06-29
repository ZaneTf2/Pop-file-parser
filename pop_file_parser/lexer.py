"""
Лексический анализатор для pop файлов.
"""
from dataclasses import dataclass
from typing import List, Optional

@dataclass
class Token:
    """Представляет токен в pop файле."""
    type: str
    value: str
    line: int
    column: int

class Lexer:
    """Лексический анализатор для pop файлов."""
    
    def __init__(self):
        self.text = ""
        self.pos = 0
        self.line = 1
        self.column = 1
        self.current_char = None
        
    def init(self, text: str) -> None:
        """Инициализирует анализатор с текстом."""
        self.text = text
        self.pos = 0
        self.line = 1
        self.column = 1
        self.current_char = text[0] if text else None
        
    def error(self) -> None:
        """Вызывает ошибку лексического анализа."""
        raise Exception(f'Lexical error at line {self.line}, column {self.column}')

    def advance(self) -> None:
        """Переходит к следующему символу."""
        self.pos += 1
        self.column += 1
        
        if self.pos > len(self.text) - 1:
            self.current_char = None
        else:
            if self.text[self.pos] == '\n':
                self.line += 1
                self.column = 0
            self.current_char = self.text[self.pos]
            
    def skip_whitespace(self) -> None:
        """Пропускает пробельные символы."""
        while (
            self.current_char is not None and 
            self.current_char.isspace()
        ):
            self.advance()
            
    def skip_comment(self) -> None:
        """Пропускает комментарии."""
        while (
            self.current_char is not None and 
            self.current_char != '\n'
        ):
            self.advance()
            
    def string(self) -> Token:
        """Обрабатывает строковые литералы."""
        result = ''
        line = self.line
        column = self.column
        
        # Пропускаем начальную кавычку
        self.advance()
        
        while (
            self.current_char is not None and 
            self.current_char != '"'
        ):
            if self.current_char == '\\':
                self.advance()
                if self.current_char == 'n':
                    result += '\n'
                elif self.current_char == 't':
                    result += '\t'
                elif self.current_char == '"':
                    result += '"'
                else:
                    result += self.current_char
            else:
                result += self.current_char
            self.advance()
            
        # Пропускаем закрывающую кавычку
        self.advance()
        
        return Token('STRING', result, line, column)
        
    def number(self) -> Token:
        """Обрабатывает числовые литералы."""
        result = ''
        line = self.line
        column = self.column
        
        while (
            self.current_char is not None and 
            (self.current_char.isdigit() or self.current_char == '.')
        ):
            result += self.current_char
            self.advance()
            
        if '.' in result:
            return Token('FLOAT', float(result), line, column)
        return Token('INTEGER', int(result), line, column)
        
    def identifier(self) -> Token:
        """Обрабатывает идентификаторы."""
        result = ''
        line = self.line
        column = self.column
        
        while (
            self.current_char is not None and 
            (self.current_char.isalnum() or self.current_char == '_')
        ):
            result += self.current_char
            self.advance()
            
        return Token('IDENTIFIER', result, line, column)
        
    def get_next_token(self) -> Optional[Token]:
        """Получает следующий токен."""
        while self.current_char is not None:
            
            # Пропускаем пробелы
            if self.current_char.isspace():
                self.skip_whitespace()
                continue
                
            # Пропускаем комментарии
            if self.current_char == '/' and self.pos + 1 < len(self.text):
                if self.text[self.pos + 1] == '/':
                    self.skip_comment()
                    continue
                    
            # Строковые литералы
            if self.current_char == '"':
                return self.string()
                
            # Числовые литералы
            if self.current_char.isdigit():
                return self.number()
                
            # Идентификаторы
            if self.current_char.isalpha() or self.current_char == '_':
                return self.identifier()
                
            # Специальные символы
            if self.current_char == '{':
                token = Token('LBRACE', '{', self.line, self.column)
                self.advance()
                return token
                
            if self.current_char == '}':
                token = Token('RBRACE', '}', self.line, self.column)
                self.advance()
                return token
                
            if self.current_char == '[':
                token = Token('LBRACKET', '[', self.line, self.column)
                self.advance()
                return token
                
            if self.current_char == ']':
                token = Token('RBRACKET', ']', self.line, self.column)
                self.advance()
                return token
                
            self.error()
            
        return Token('EOF', None, self.line, self.column)
        
    def tokenize(self, text: str) -> List[Token]:
        """Разбивает текст на токены."""
        self.init(text)
        tokens = []
        
        token = self.get_next_token()
        while token.type != 'EOF':
            tokens.append(token)
            token = self.get_next_token()
            
        tokens.append(token)
        return tokens

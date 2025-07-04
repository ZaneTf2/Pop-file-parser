"""
Тесты для лексического анализатора.
"""
import pytest
from pop_file_parser.lexer import Lexer, Token

@pytest.fixture
def lexer():
    """Фикстура для создания лексера."""
    return Lexer()

def test_tokenize_string():
    """Тест токенизации строки."""
    lexer = Lexer()
    tokens = lexer.tokenize('"Hello World"')
    
    assert len(tokens) == 2  # STRING + EOF
    assert tokens[0].type == 'STRING'
    assert tokens[0].value == 'Hello World'

def test_tokenize_number():
    """Тест токенизации чисел."""
    lexer = Lexer()
    
    # Целое число
    tokens = lexer.tokenize('42')
    assert len(tokens) == 2  # INTEGER + EOF
    assert tokens[0].type == 'INTEGER'
    assert tokens[0].value == 42
    
    # Число с плавающей точкой
    tokens = lexer.tokenize('3.14')
    assert len(tokens) == 2  # FLOAT + EOF
    assert tokens[0].type == 'FLOAT'
    assert tokens[0].value == 3.14

def test_tokenize_identifier():
    """Тест токенизации идентификаторов."""
    lexer = Lexer()
    tokens = lexer.tokenize('Wave123_test')
    
    assert len(tokens) == 2  # IDENTIFIER + EOF
    assert tokens[0].type == 'IDENTIFIER'
    assert tokens[0].value == 'Wave123_test'

def test_tokenize_braces():
    """Тест токенизации фигурных скобок."""
    lexer = Lexer()
    tokens = lexer.tokenize('{}')
    
    assert len(tokens) == 3  # LBRACE + RBRACE + EOF
    assert tokens[0].type == 'LBRACE'
    assert tokens[1].type == 'RBRACE'

def test_tokenize_brackets():
    """Тест токенизации квадратных скобок."""
    lexer = Lexer()
    tokens = lexer.tokenize('[]')
    
    assert len(tokens) == 3  # LBRACKET + RBRACKET + EOF
    assert tokens[0].type == 'LBRACKET'
    assert tokens[1].type == 'RBRACKET'

def test_tokenize_complex():
    """Тест токенизации сложного выражения."""
    lexer = Lexer()
    tokens = lexer.tokenize('{"Name": "Heavy", "Health": 300}')
    
    expected_types = [
        'LBRACE', 
        'STRING',  # "Name"
        'STRING',  # "Heavy"
        'STRING',  # "Health"
        'INTEGER', # 300
        'RBRACE',
        'EOF'
    ]
    
    assert len(tokens) == len(expected_types)
    for token, expected_type in zip(tokens, expected_types):
        assert token.type == expected_type

def test_tokenize_with_comments():
    """Тест токенизации с комментариями."""
    lexer = Lexer()
    tokens = lexer.tokenize('''
        // This is a comment
        {
            "Name": "Heavy" // Another comment
        }
    ''')
    
    expected_types = [
        'LBRACE',
        'STRING',  # "Name"
        'STRING',  # "Heavy"
        'RBRACE',
        'EOF'
    ]
    
    assert len(tokens) == len(expected_types)
    for token, expected_type in zip(tokens, expected_types):
        assert token.type == expected_type

def test_tokenize_invalid():
    """Тест обработки некорректного ввода."""
    lexer = Lexer()
    
    with pytest.raises(Exception):
        lexer.tokenize('$')  # Неподдерживаемый символ

def test_line_column_tracking():
    """Тест отслеживания строк и столбцов."""
    lexer = Lexer()
    tokens = lexer.tokenize('''
        {
            "Name": "Heavy"
        }
    ''')
    
    # Проверяем позицию открывающей скобки
    assert tokens[0].line > 1  # Должна быть после первой строки
    assert tokens[0].column > 1  # Должна быть после пробелов

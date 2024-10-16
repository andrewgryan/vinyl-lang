import pytest
from compiler.lexer import lex, Token, TokenKind


@pytest.mark.parametrize(
    "content,tokens",
    [
        ("", []),
        (";", [Token(TokenKind.SEMICOLON, ";")]),
        ("=", [Token(TokenKind.EQUAL, "=")]),
        ("(", [Token(TokenKind.LEFT_PAREN, "(")]),
        (")", [Token(TokenKind.RIGHT_PAREN, ")")]),
        ("{", [Token(TokenKind.OPEN_BRACE, "{")]),
        ("}", [Token(TokenKind.CLOSE_BRACE, "}")]),
        ("+", [Token(TokenKind.PLUS, "+")]),
        ("-", [Token(TokenKind.MINUS, "-")]),
        ("*", [Token(TokenKind.STAR, "*")]),
        ("/", [Token(TokenKind.FORWARD_SLASH, "/")]),
        ("^", [Token(TokenKind.CARET, "^")]),
        ("fn", [Token(TokenKind.FUNCTION, "fn")]),
        ("main", [Token(TokenKind.IDENTIFIER, "main")]),
        ("print", [Token(TokenKind.PRINT, "print")]),
    ],
)
def test_lex(content, tokens):
    assert list(lex(content)) == tokens

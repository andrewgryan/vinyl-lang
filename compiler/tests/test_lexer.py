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
    ],
)
def test_lex(content, tokens):
    assert list(lex(content)) == tokens

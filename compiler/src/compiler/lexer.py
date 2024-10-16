from dataclasses import dataclass
from enum import Enum


class TokenKind(Enum):
    COMMENT = 1
    LEFT_PAREN = 2
    RIGHT_PAREN = 3
    SEMICOLON = 4
    EXIT = 5
    INT = 6
    LET = 7
    EQUAL = 8
    IDENTIFIER = 9
    OPEN_BRACE = 10
    CLOSE_BRACE = 11
    PLUS = 12
    MINUS = 13
    STAR = 14
    FORWARD_SLASH = 15
    CARET = 16
    FUNCTION = 17
    PRINT = 18


@dataclass
class Token:
    kind: TokenKind
    text: str

    @classmethod
    def identifier(cls, text: str):
        return cls(kind=TokenKind.IDENTIFIER, text=text)

    @classmethod
    def int(cls, text: str):
        return cls(kind=TokenKind.INT, text=text)

    @classmethod
    def plus(cls):
        return cls(kind=TokenKind.PLUS, text="+")


def lex_comment(cursor, content):
    begin = cursor
    while cursor < len(content):
        if content[cursor] == "\n":
            break
        cursor += 1
    token = Token(
        kind=TokenKind.COMMENT, text=content[begin : cursor + 1]
    )
    return cursor + 1, token


def lex_int(cursor, content):
    begin = cursor
    while cursor < len(content):
        if content[cursor].isdigit():
            cursor += 1
        else:
            break
    token = Token.int(content[begin:cursor])
    return cursor, token


def lex_identifier(cursor, content):
    begin = cursor

    # First char [a-zA-Z]
    if not content[begin].isalpha():
        return cursor, None

    # All other chars [a-zA-Z0-9]
    while cursor < len(content):
        if content[cursor].isalnum():
            cursor += 1
        else:
            break

    token = Token.identifier(content[begin:cursor])
    return cursor, token


def lex_keyword(key, cursor, content):
    kinds = {
        "let": TokenKind.LET,
        "exit": TokenKind.EXIT,
        "fn": TokenKind.FUNCTION,
        "print": TokenKind.PRINT,
    }
    length = len(key)
    token = Token(
        kind=kinds[key],
        text=content[cursor : cursor + length],
    )
    return cursor + length, token


def lex(content):
    cursor = 0
    chars = {
        ";": TokenKind.SEMICOLON,
        "=": TokenKind.EQUAL,
        "(": TokenKind.LEFT_PAREN,
        ")": TokenKind.RIGHT_PAREN,
        "{": TokenKind.OPEN_BRACE,
        "}": TokenKind.CLOSE_BRACE,
        "+": TokenKind.PLUS,
        "-": TokenKind.MINUS,
        "*": TokenKind.STAR,
        "/": TokenKind.FORWARD_SLASH,
        "^": TokenKind.CARET,
    }
    while cursor < len(content):
        if content[cursor] == "#":
            cursor, token = lex_comment(cursor, content)
            yield token
        elif content[cursor].isdigit():
            cursor, token = lex_int(cursor, content)
            yield token
        elif content[cursor:].startswith("exit"):
            cursor, token = lex_keyword("exit", cursor, content)
            yield token
        elif content[cursor:].startswith("let"):
            cursor, token = lex_keyword("let", cursor, content)
            yield token
        elif content[cursor:].startswith("fn"):
            cursor, token = lex_keyword("fn", cursor, content)
            yield token
        elif content[cursor:].startswith("print"):
            cursor, token = lex_keyword("print", cursor, content)
            yield token
        elif content[cursor].isalpha():
            cursor, token = lex_identifier(cursor, content)
            yield token
        elif content[cursor] in chars:
            token = Token(
                kind=chars[content[cursor]], text=content[cursor]
            )
            yield token
            cursor += 1
        else:
            cursor += 1

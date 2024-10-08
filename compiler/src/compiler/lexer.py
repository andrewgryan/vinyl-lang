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


def lex_exit(cursor, content):
    token = Token(
        kind=TokenKind.EXIT, text=content[cursor : cursor + 4]
    )
    return cursor + 4, token


def lex_let(cursor, content):
    length = len("let")
    token = Token(
        kind=TokenKind.LET,
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
    }
    while cursor < len(content):
        if content[cursor] == "#":
            cursor, token = lex_comment(cursor, content)
            yield token
        elif content[cursor].isdigit():
            cursor, token = lex_int(cursor, content)
            yield token
        elif content[cursor : cursor + 4] == "exit":
            cursor, token = lex_exit(cursor, content)
            yield token
        elif content[cursor:].startswith("let"):
            cursor, token = lex_let(cursor, content)
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

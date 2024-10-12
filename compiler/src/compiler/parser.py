from __future__ import annotations
from enum import Enum
from collections import namedtuple
from dataclasses import dataclass
from compiler.lexer import lex, Token, TokenKind


Op = namedtuple("Op", "operator precedence associative")


class Associative(Enum):
    LEFT = 1
    RIGHT = 2


OPERATORS = {
    "+": Op("+", 1, Associative.LEFT),
    "-": Op("-", 1, Associative.LEFT),
    "*": Op("*", 2, Associative.LEFT),
    "/": Op("/", 2, Associative.LEFT),
    "^": Op("^", 3, Associative.RIGHT),
}

@dataclass
class NodeLiteral:
    value: Token

@dataclass
class NodeBinOp:
    operator: str
    lhs: NodeBinOp | NodeLiteral = None
    rhs: NodeBinOp | NodeLiteral = None


def parse_op(tokens, cursor):
    if tokens[cursor].text in OPERATORS:
        return OPERATORS[tokens[cursor].text], cursor + 1
    else:
        return None, cursor


def literal(value):
    return NodeInt(Token.int(value))


@dataclass
class NodeExpression:
    tokens: list[Token]


@dataclass
class NodeAdd:
    lhs: NodeExpression
    rhs: NodeExpression


@dataclass
class NodeInt:
    token: Token


@dataclass
class NodeIdentifier:
    token: Token


@dataclass
class NodeExit:
    status: NodeInt | NodeIdentifier


@dataclass
class NodeLet:
    identifier: Token
    value: Token


NodeStatement = NodeLet | NodeExit


@dataclass
class NodeProgram:
    statements: list[NodeStatement]


@dataclass
class NodeBlock:
    statements: list[NodeStatement]


def parse(content: str):
    tokens = list(lex(content))
    cursor = 0
    statements = []
    while cursor < len(tokens):
        statement, cursor = parse_statement(tokens, cursor)
        if statement:
            statements.append(statement)
            continue
        else:
            cursor += 1
    return NodeProgram(statements)


def parse_binary(tokens, cursor):
    op, _ = parse_op(tokens, cursor + 1)
    if tokens[cursor].kind == TokenKind.INT:
        lhs = NodeInt(tokens[cursor])
    if tokens[cursor + 2].kind == TokenKind.INT:
        rhs = NodeInt(tokens[cursor + 2])
    if op:
        return NodeBinOp(op, lhs, rhs), cursor
    else:
        return None, cursor


def parse_block(tokens, cursor):
    if tokens[cursor].kind == TokenKind.OPEN_BRACE:
        cursor += 1
        statements = []
        while (cursor < len(tokens)) and (
            tokens[cursor].kind != TokenKind.CLOSE_BRACE
        ):
            statement, cursor = parse_statement(tokens, cursor)
            if statement:
                statements.append(statement)
            else:
                cursor += 1
        return NodeBlock(statements), cursor
    else:
        return None, cursor


def parse_statement(tokens, cursor):
    statement, cursor = parse_exit(tokens, cursor)
    if statement:
        return statement, cursor
    statement, cursor = parse_let(tokens, cursor)
    if statement:
        return statement, cursor
    statement, cursor = parse_block(tokens, cursor)
    if statement:
        return statement, cursor
    return None, cursor


def exit(status: str):
    return NodeExit(NodeInt(Token.int(status)))


def parse_exit(tokens, cursor):
    if (
        (tokens[cursor + 0].kind == TokenKind.EXIT)
        and (tokens[cursor + 1].kind == TokenKind.LEFT_PAREN)
        and (tokens[cursor + 3].kind == TokenKind.RIGHT_PAREN)
        and (tokens[cursor + 4].kind == TokenKind.SEMICOLON)
    ):
        status, cursor = parse_expression(tokens, cursor + 2)
        return NodeExit(status=status), cursor + 2
    else:
        return None, cursor


def let(identifier: str, value: str):
    return NodeLet(
        Token.identifier(identifier), Token.int(value)
    )


def parse_let(tokens, cursor):
    # let identifier = expression;
    if (
        (tokens[cursor].kind == TokenKind.LET)
        and (tokens[cursor + 1].kind == TokenKind.IDENTIFIER)
        and (tokens[cursor + 2].kind == TokenKind.EQUAL)
    ):
        identifier = tokens[cursor + 1]
        expression, next_cursor = parse_arithmetic(tokens, cursor + 3)
        if expression and (tokens[next_cursor].kind == TokenKind.SEMICOLON):
            return NodeLet(identifier, expression), next_cursor + 1
        else:
            return None, cursor
    else:
        return None, cursor


def parse_arithmetic(tokens, cursor):
    if tokens[cursor].kind == TokenKind.INT:
        return tokens[cursor], cursor + 1
    else:
        return None, cursor


def parse_expression(tokens, cursor):
    # TODO: Support arithmetic expressions
    if tokens[cursor].kind == TokenKind.INT:
        return NodeInt(tokens[cursor]), cursor + 1
    elif tokens[cursor].kind == TokenKind.IDENTIFIER:
        return NodeIdentifier(tokens[cursor]), cursor + 1
    else:
        return None, cursor

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


def literal(value):
    return NodeInt(Token.int(value))


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
class NodePrint:
    message: NodeInt


@dataclass
class NodeLet:
    identifier: NodeIdentifier
    value: Token


NodeStatement = NodeLet | NodeExit


@dataclass
class NodeProgram:
    statements: list[NodeStatement]


@dataclass
class NodeBlock:
    statements: list[NodeStatement]


@dataclass
class NodeFunction:
    identifier: NodeIdentifier
    body: NodeBlock


@dataclass
class NodeCall:
    identifier: NodeIdentifier


@dataclass
class NodeReturn:
    expression: str


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


def parse_block(tokens, cursor):
    original_cursor = cursor
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
        return NodeBlock(statements), cursor + 1
    else:
        return None, original_cursor


def parse_statement(tokens, cursor):
    statement, cursor = parse_function(tokens, cursor)
    if statement:
        return statement, cursor
    statement, cursor = parse_exit(tokens, cursor)
    if statement:
        return statement, cursor
    statement, cursor = parse_print(tokens, cursor)
    if statement:
        return statement, cursor
    statement, cursor = parse_return(tokens, cursor)
    if statement:
        return statement, cursor
    statement, cursor = parse_call(tokens, cursor)
    if statement:
        return statement, cursor
    statement, cursor = parse_let(tokens, cursor)
    if statement:
        return statement, cursor
    statement, cursor = parse_block(tokens, cursor)
    if statement:
        return statement, cursor
    return None, cursor


def parse_function(tokens, cursor):
    original_cursor = cursor
    if peek(tokens, cursor).kind == TokenKind.FUNCTION:
        _, cursor = consume(tokens, cursor)
        identifier, cursor = parse_identifier(tokens, cursor)
        token, cursor = consume(tokens, cursor)
        if token.kind != TokenKind.LEFT_PAREN:
            return False, original_cursor
        token, cursor = consume(tokens, cursor)
        if token.kind != TokenKind.RIGHT_PAREN:
            return False, original_cursor
        block, cursor = parse_block(tokens, cursor)
        return NodeFunction(identifier, block), cursor
    else:
        return False, original_cursor


def parse_identifier(tokens, cursor):
    if peek(tokens, cursor).kind == TokenKind.IDENTIFIER:
        token, cursor = consume(tokens, cursor)
        return NodeIdentifier(token), cursor
    else:
        return False, cursor


def peek(tokens, cursor):
    return tokens[cursor]


def consume(tokens, cursor):
    return tokens[cursor], cursor + 1


def exit(status: str):
    return NodeExit(NodeInt(Token.int(status)))


def parse_exit(tokens, cursor):
    if (tokens[cursor + 0].kind == TokenKind.EXIT) and (
        tokens[cursor + 1].kind == TokenKind.LEFT_PAREN
    ):
        status, next_cursor = parse_expression(
            tokens, cursor + 2
        )
        if (
            status
            and (
                tokens[next_cursor + 0].kind
                == TokenKind.RIGHT_PAREN
            )
            and (
                tokens[next_cursor + 1].kind
                == TokenKind.SEMICOLON
            )
        ):
            return NodeExit(status=status), next_cursor + 2
    return None, cursor


def parse_print(tokens, cursor):
    if peek(tokens, cursor).kind == TokenKind.PRINT:
        _, cursor = consume(tokens, cursor)

        token, cursor = consume(tokens, cursor)
        if token.kind != TokenKind.LEFT_PAREN:
            return False, cursor

        message, cursor = parse_expression(tokens, cursor)

        token, cursor = consume(tokens, cursor)
        if token.kind != TokenKind.RIGHT_PAREN:
            return False, cursor

        token, cursor = consume(tokens, cursor)
        if token.kind != TokenKind.SEMICOLON:
            return False, cursor

        return NodePrint(message), cursor
    else:
        return False, cursor


def parse_call(tokens, cursor):
    if peek(tokens, cursor).kind == TokenKind.IDENTIFIER:
        identifier, cursor = consume(tokens, cursor)

        token, cursor = consume(tokens, cursor)
        if token.kind != TokenKind.LEFT_PAREN:
            return False, cursor

        token, cursor = consume(tokens, cursor)
        if token.kind != TokenKind.RIGHT_PAREN:
            return False, cursor

        token, cursor = consume(tokens, cursor)
        if token.kind != TokenKind.SEMICOLON:
            return False, cursor

        return NodeCall(NodeIdentifier(identifier)), cursor
    else:
        return False, cursor


def parse_return(tokens, cursor):
    if peek(tokens, cursor).kind == TokenKind.RETURN:
        _, cursor = consume(tokens, cursor)
        expression, cursor = parse_expression(tokens, cursor)
        return NodeReturn(expression), cursor
    else:
        return False, cursor


def let(identifier: str, value: str):
    return NodeLet(
        NodeIdentifier(Token.identifier(identifier)),
        NodeInt(Token.int(value)),
    )


def parse_let(tokens, cursor):
    # let identifier = expression;
    if (
        (tokens[cursor].kind == TokenKind.LET)
        and (tokens[cursor + 1].kind == TokenKind.IDENTIFIER)
        and (tokens[cursor + 2].kind == TokenKind.EQUAL)
    ):
        identifier = NodeIdentifier(tokens[cursor + 1])
        expression, next_cursor = parse_expression(
            tokens, cursor + 3
        )
        if expression and (
            tokens[next_cursor].kind == TokenKind.SEMICOLON
        ):
            return (
                NodeLet(identifier, expression),
                next_cursor + 1,
            )
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
    if tokens[cursor].kind == TokenKind.INT:
        node, next_cursor = parse_binary(tokens, cursor)
        if node:
            return node, next_cursor
        else:
            return NodeInt(tokens[cursor]), cursor + 1
    elif tokens[cursor].kind == TokenKind.IDENTIFIER:
        return NodeIdentifier(tokens[cursor]), cursor + 1
    else:
        return None, cursor


def parse_binary(tokens, cursor):
    # (((((a) + b) + c) + d) + e)
    lhs, cursor = parse_term(tokens, cursor)
    op, cursor = parse_op(tokens, cursor)
    while (cursor < len(tokens)) and op:
        rhs, cursor = parse_term(tokens, cursor)
        lhs = NodeBinOp(op, lhs, rhs)
        op, cursor = parse_op(tokens, cursor)
    return lhs, cursor


def parse_term(tokens, cursor):
    if (cursor < len(tokens)) and tokens[
        cursor
    ].kind == TokenKind.INT:
        return NodeInt(tokens[cursor]), cursor + 1
    else:
        return None, cursor


def parse_op(tokens, cursor):
    if cursor >= len(tokens):
        return None, cursor
    if tokens[cursor].text in OPERATORS:
        return OPERATORS[tokens[cursor].text], cursor + 1
    else:
        return None, cursor

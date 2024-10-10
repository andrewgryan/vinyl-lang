from dataclasses import dataclass
from compiler.lexer import lex, Token, TokenKind


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
        if tokens[cursor].kind == TokenKind.OPEN_BRACE:
            block, cursor = parse_block(tokens, cursor)
            if block:
                statements.append(block)
                continue

        statement, cursor = parse_exit(tokens, cursor)
        if statement:
            statements.append(statement)
            continue
        statement, cursor = parse_let(tokens, cursor)
        if statement:
            statements.append(statement)
            continue
        else:
            cursor += 1
    return NodeProgram(statements)


def parse_block(tokens, cursor):
    return NodeBlock([]), cursor + 1


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
    rule = (
        TokenKind.LET,
        TokenKind.IDENTIFIER,
        TokenKind.EQUAL,
        TokenKind.INT,
        TokenKind.SEMICOLON,
    )
    kinds = tuple(
        token.kind for token in tokens[cursor : cursor + 5]
    )
    if rule == kinds:
        node = NodeLet(tokens[cursor + 1], tokens[cursor + 3])
        return node, cursor + 5
    else:
        return None, cursor


def parse_expression(tokens, cursor):
    if tokens[cursor].kind == TokenKind.INT:
        return NodeInt(tokens[cursor]), cursor + 1
    elif tokens[cursor].kind == TokenKind.IDENTIFIER:
        return NodeIdentifier(tokens[cursor]), cursor + 1
    else:
        return None, cursor

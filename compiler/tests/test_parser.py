import pytest
from compiler.lexer import lex
from compiler.parser import (
    parse,
    parse_binary,
    add,
    literal,
    let,
    exit,
    NodeLet,
    NodeBlock,
    NodeExit,
    NodeExpression,
    NodeIdentifier,
    Token,
)


@pytest.mark.parametrize(
    "content,statements",
    [
        ("", []),
        ("# Comment", []),
        (";", []),
        ("let foo = 42;", [let("foo", "42")]),
        ("exit(42);", [exit("42")]),
        (
            "exit(foo);",
            [
                NodeExit(
                    status=NodeIdentifier(
                        Token.identifier("foo")
                    )
                )
            ],
        ),
        ("{}", [NodeBlock([])]),
        ("{let x = 1;}", [NodeBlock([let("x", "1")])]),
        (
            "let y = 2;\n{\nlet x = 1;\n}\n",
            [let("y", "2"), NodeBlock([let("x", "1")])],
        ),
        pytest.param(
            "let x = 1 + 1;",
            [
                NodeLet(
                    identifier=NodeIdentifier(
                        Token.identifier("x")
                    ),
                    value=NodeExpression(
                        [
                            Token.int("1"),
                            Token.plus(),
                            Token.int("1"),
                        ]
                    ),
                )
            ],
            marks=pytest.mark.xfail
        ),
    ],
)
def test_parse(content, statements):
    assert parse(content).statements == statements


@pytest.mark.parametrize(
    "code,ast",
    [
        ("1 + 1", add(literal("1"), literal("1")))
    ]
)
def test_parse_binary_expression(code, ast):
    tokens = list(lex(code))
    node, _ = parse_binary(tokens, 0)
    assert node == ast

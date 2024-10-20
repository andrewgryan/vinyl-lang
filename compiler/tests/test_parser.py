import pytest
from compiler import parser
from compiler.lexer import lex
from compiler.parser import (
    parse,
    parse_op,
    parse_binary,
    literal,
    let,
    exit,
    NodeLet,
    NodeBlock,
    NodeBinOp,
    NodeExit,
    NodeExpression,
    NodeIdentifier,
    NodeFunction,
    Token,
    Op,
    Associative,
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
            "exit(1 + 2);",
            [
                NodeExit(
                    NodeBinOp(
                        Op("+", 1, Associative.LEFT),
                        literal("1"),
                        literal("2"),
                    )
                )
            ],
        ),
        pytest.param(
            "let x = 1 + 2;",
            [
                NodeLet(
                    identifier=NodeIdentifier(
                        Token.identifier("x")
                    ),
                    value=NodeBinOp(
                        Op("+", 1, Associative.LEFT),
                        literal("1"),
                        literal("2"),
                    ),
                )
            ],
            marks=pytest.mark.skip("wip"),
        ),
        pytest.param(
            "fn foo() {}",
            [
                NodeFunction(
                    NodeIdentifier(Token.identifier("foo")),
                    NodeBlock([]),
                )
            ],
        ),
        pytest.param(
            "print(42);",
            [parser.NodePrint(parser.NodeInt(Token.int("42")))],
        ),
        pytest.param(
            "foo();",
            [
                parser.NodeCall(
                    NodeIdentifier(Token.identifier("foo"))
                )
            ],
        ),
        pytest.param(
            "print(x);",
            [
                parser.NodePrint(
                    parser.NodeIdentifier(Token.identifier("x"))
                )
            ],
        ),
    ],
)
def test_parse(content, statements):
    assert parse(content).statements == statements


@pytest.mark.parametrize(
    "code,ast",
    [
        ("1", literal("1")),
        (
            "1 + 1",
            NodeBinOp(
                Op("+", 1, Associative.LEFT),
                literal("1"),
                literal("1"),
            ),
        ),
        (
            "1 - 1",
            NodeBinOp(
                Op("-", 1, Associative.LEFT),
                literal("1"),
                literal("1"),
            ),
        ),
        (
            "1 + 2 + 3",
            NodeBinOp(
                Op("+", 1, Associative.LEFT),
                NodeBinOp(
                    Op("+", 1, Associative.LEFT),
                    literal("1"),
                    literal("2"),
                ),
                literal("3"),
            ),
        ),
        (
            "1 - 2 + 3",
            NodeBinOp(
                Op("+", 1, Associative.LEFT),
                NodeBinOp(
                    Op("-", 1, Associative.LEFT),
                    literal("1"),
                    literal("2"),
                ),
                literal("3"),
            ),
        ),
        (
            "1 + 2 + 3 + 4",
            NodeBinOp(
                Op("+", 1, Associative.LEFT),
                NodeBinOp(
                    Op("+", 1, Associative.LEFT),
                    NodeBinOp(
                        Op("+", 1, Associative.LEFT),
                        literal("1"),
                        literal("2"),
                    ),
                    literal("3"),
                ),
                literal("4"),
            ),
        ),
    ],
)
def test_parse_binary_expression(code, ast):
    tokens = list(lex(code))
    node, _ = parse_binary(tokens, 0)
    assert node == ast


def test_parse_op():
    tokens = list(lex("10 * 2 ^ 8"))
    assert parse_op(tokens, 1)[0] == Op("*", 2, Associative.LEFT)
    assert parse_op(tokens, 3)[0] == Op(
        "^", 3, Associative.RIGHT
    )

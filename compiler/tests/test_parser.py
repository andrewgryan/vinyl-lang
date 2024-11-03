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
                    [],
                    NodeBlock([]),
                )
            ],
        ),
        pytest.param(
            "fn bar(y) {}",
            [
                NodeFunction(
                    identifier=NodeIdentifier(
                        Token.identifier("bar")
                    ),
                    parameters=[
                        NodeIdentifier(Token.identifier("y"))
                    ],
                    body=NodeBlock([]),
                )
            ],
        ),
        pytest.param(
            "fn baz(a, b, c) {}",
            [
                NodeFunction(
                    identifier=NodeIdentifier(
                        Token.identifier("baz")
                    ),
                    parameters=[
                        NodeIdentifier(Token.identifier("a")),
                        NodeIdentifier(Token.identifier("b")),
                        NodeIdentifier(Token.identifier("c")),
                    ],
                    body=NodeBlock([]),
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
                    NodeIdentifier(Token.identifier("foo")), []
                )
            ],
        ),
        pytest.param(
            "bar(99);",
            [
                parser.NodeCall(
                    NodeIdentifier(Token.identifier("bar")),
                    [parser.NodeInt(Token.int("99"))],
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
        pytest.param(
            "return 5;",
            [parser.NodeReturn(parser.NodeInt(Token.int("5")))],
        ),
        pytest.param(
            "let y = x + 1;",
            [
                parser.NodeLet(
                    parser.NodeIdentifier(Token.identifier("y")),
                    parser.NodeBinOp(
                        Op("+", 1, Associative.LEFT),
                        parser.NodeIdentifier(
                            Token.identifier("x")
                        ),
                        parser.NodeInt(Token.int("1")),
                    ),
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

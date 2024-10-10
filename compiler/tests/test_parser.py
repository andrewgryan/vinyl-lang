import pytest
from compiler.parser import (
    parse,
    let,
    exit,
    NodeBlock,
    NodeExit,
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
        ("let y = 2;\n{\nlet x = 1;\n}\n", [let("y", "2"), NodeBlock([let("x", "1")])]),
    ],
)
def test_parse(content, statements):
    assert parse(content).statements == statements

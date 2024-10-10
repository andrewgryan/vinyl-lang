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
    ],
)
def test_parse(content, statements):
    assert parse(content).statements == statements

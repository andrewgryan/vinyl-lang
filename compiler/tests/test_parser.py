import pytest
from compiler.main import parse, let, exit


@pytest.mark.parametrize("content,statements", [
    ("", []),
    ("# Comment", []),
    (";", []),
    ("let foo = 42;", [let("foo", "42")]),
    ("exit(42);", [exit("42")])
])
def test_parse(content, statements):
    assert parse(content).statements == statements

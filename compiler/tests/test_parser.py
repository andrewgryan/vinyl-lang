import pytest
from compiler.main import parse, let


@pytest.mark.parametrize("content,statements", [
    ("", []),
    ("# Comment", []),
    (";", []),
    ("let foo = 42;", [let("foo", "42")])
])
def test_parse(content, statements):
    assert parse(content).statements == statements

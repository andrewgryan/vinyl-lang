import pytest
from pytest import param
from compiler import pseudo
from compiler.pseudo import (
    Add,
    AST,
    Call,
    Fn,
    Int,
    Id,
    Return,
    register,
    parameter,
)


def test_pseudo_code_return():
    ast = AST([Return(Int(0))])
    visitor = pseudo.Visitor()
    actual = visitor.visit(ast)
    expected = [
        ("mov", register(0), 0),
        ("mov", "rax", register(0)),
    ]
    assert actual == expected


def test_pseudo_code_call():
    ast = AST([Call(Id("bar"), [Int(2)])])
    visitor = pseudo.Visitor()
    actual = visitor.visit(ast)
    expected = [
        ("mov", register(0), 2),
        ("mov", parameter(0), register(0)),
        ("call", "bar"),
    ]
    assert actual == expected


@pytest.mark.parametrize(
    "program,expected",
    [
        param(
            AST([Fn(Id("bar"), [], [])]),
            [("label", "bar")],
            id="fn-empty-body",
        ),
        param(
            AST([Fn(Id("bar"), [Id("x")], [Return(Id("x"))])]),
            [
                ("label", "bar"),
                ("prolog", 8),
                ("mov", base_pointer(-8), parameter(1))
                ("mov", "return_register", base_pointer(-8))
                ("epilog", 8),
                ("ret")
            ],
            id="fn-return-x",
        ),
    ],
)
def test_pseudo_code_fn(program, expected):
    visitor = pseudo.Visitor()
    actual = visitor.visit(program)
    assert actual == expected

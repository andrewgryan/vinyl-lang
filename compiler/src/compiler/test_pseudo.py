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


def test_pseudo_code_fn():
    ast = AST([Fn(Id("bar"), [], [])])
    visitor = pseudo.Visitor()
    actual = visitor.visit(ast)
    expected = [("label", "bar")]
    assert actual == expected

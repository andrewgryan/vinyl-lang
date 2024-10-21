from compiler import ir, parser
import pytest


@pytest.mark.parametrize(
    "code,expected",
    [
        ("return 5;", [(ir.RETF, ir.Lit(5))]),
        (
            "let x = 1;let y = 2;",
            [
                (ir.COPY, ir.Lit(1), ir.Var("x", "u32", "_start")),
                (ir.COPY, ir.Lit(2), ir.Var("y", "u32", "_start")),
            ],
        ),
    ],
)
def test_ir(code, expected):
    ast = parser.parse(code)
    actual = ir.translate(ast)
    assert actual == expected

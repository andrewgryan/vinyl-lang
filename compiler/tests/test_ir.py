from compiler import ir, parser, code_gen
import pytest


@pytest.mark.parametrize(
    "statements,instructions",
    [
        (
            ["let x = 3;", "exit(0);"],
            [
                ("global", "start", None, None),
                ("section", "text", None, None),
                ("label", "_start", None, None),
                ("=", "x", 3, None),
                ("exit", 0, None, None),
            ],
        ),
        (
            ["fn main() {", "return 5;", "}", "main();"],
            [
                ("global", "start", None, None),
                ("section", "text", None, None),
                ("label", "main", None, None),
                ("return", 5, None, None),
                ("ret", None, None, None),
                ("label", "_start", None, None),
                ("call", "main", None, None),
            ],
        ),
        pytest.param(
            ["foo(7);"],
            [
                ("global", "start", None, None),
                ("section", "text", None, None),
                ("label", "_start", None, None),
                ("store", "parameter", 1, 7),
                ("call", "foo", None, None),
            ],
            marks=pytest.mark.skip("implementing parser"),
        )
    ],
)
def test_visitor(statements, instructions):
    ast = parser.parse("\n".join(statements))
    assert list(ir.visit(ast)) == instructions


def test_visitor_main_program():
    ast = parser.parse(
        """
        fn main() {
            return 42;
        }
        main();
    """
    )
    assert list(ir.visit(ast)) == [
        ("global", "start", None, None),
        ("section", "text", None, None),
        ("label", "main", None, None),
        ("return", 42, None, None),
        ("ret", None, None, None),
        ("label", "_start", None, None),
        ("call", "main", None, None),
    ]


def test_ir_code_gen():
    instructions = [("=", "x", 3, None), ("exit", 0, None, None)]
    assert list(code_gen.gas_lines(instructions)) == [
        "mov $3, -0x8(%rbp)",
        "mov $60, %rax",
        "mov $0, %rdi",
        "syscall",
    ]
    assert list(code_gen.aarch64_lines(instructions)) == [
        "mov [sp, #0x8], #0x3",
        "mov x8, #0x5d",
        "mov x0, #0x0",
        "svc 0",
    ]


def test_ir_return():
    instructions = [("return", 42, None, None)]
    assert list(code_gen.aarch64_lines(instructions)) == [
        "mov x0, #0x2a",
        "ret",
    ]
    assert list(code_gen.gas_lines(instructions)) == [
        "mov $42, %rax",
    ]

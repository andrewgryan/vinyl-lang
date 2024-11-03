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
            ["foo(7, 42);"],
            [
                ("global", "start", None, None),
                ("section", "text", None, None),
                ("label", "_start", None, None),
                ("store_parameter", 1, 7, None),
                ("store_parameter", 2, 42, None),
                ("call", "foo", None, None),
            ],
        ),
        pytest.param(
            ["fn foo(x) {", "return x;", "}"],
            [
                ("global", "start", None, None),
                ("section", "text", None, None),
                ("label", "foo", None, None),
                ("prolog", 8, None, None),
                ("parameter", 1, 8, None),
                ("return", ("parameter", 1, 8), None, None),
                ("epilog", 8, None, None),
                ("ret", None, None, None),
                ("label", "_start", None, None),
            ],
        ),
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
        "\tmov\t$3, -0x8(%rbp)",
        "\tmov\t$60, %rax",
        "\tmov\t$0, %rdi",
        "\tsyscall",
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
        "\tmov\t$42, %rax",
    ]


@pytest.mark.parametrize(
    "instructions,expect",
    [
        ([], []),
        (
            [("prolog", 8, None, None)],
            [
                "\tpush\t%rbp",
                "\tmov\t%rsp, %rbp",
                "\tsub\t$8, %rsp",
            ],
        ),
        (
            [("epilog", 8, None, None)],
            [
                "\tmov\t%rbp, %rsp",
                "\tpop\t%rbp",
            ],
        ),
    ],
)
def test_gas_lines(instructions, expect):
    assert list(code_gen.gas_lines(instructions)) == expect

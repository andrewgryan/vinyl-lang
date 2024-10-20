import pytest
from compiler.arch import Arch
from compiler.code_gen import code_gen, stack_alignment
from compiler.parser import parse


def test_code_gen_aarch64():
    program = parse("")
    expected = """
.global _start
.section .text

_start:
"""
    assert code_gen(program, Arch.aarch64) == expected


@pytest.mark.parametrize(
    "program",
    [
        pytest.param("exit(42);", id="exit"),
        pytest.param("let x = 42;", id="assign"),
        pytest.param("let x = 42;exit(x);", id="dereference"),
        pytest.param("let x = 42;let y = 7;exit(x);", id="vars"),
        pytest.param(
            "let x = 42;let y = 7;exit(y);", id="second_var"
        ),
        pytest.param(
            "let x = 1; { let y = 42; } exit(x);", id="block"
        ),
        pytest.param(
            "exit(1 + 2);",
            id="addition",
        ),
        pytest.param(
            "exit(3 - 1);",
            id="subtraction",
        ),
        pytest.param(
            "exit(1 + 2 + 3);",
            id="add_all",
        ),
        pytest.param(
            "exit(7 - 3 - 2);",
            id="sub_all",
        ),
        pytest.param("let x = 2 - 1;", id="assign_expr"),
        pytest.param("fn foo() { let x = 1; }", id="fn"),
        pytest.param("print(42);", id="print"),
        pytest.param("let x = 4;print(x);", id="print_let"),
        pytest.param("print(42);print(7);", id="print_x2"),
        pytest.param(
            "fn foo() { print(42); }\nfoo();", id="call_fn"
        ),
    ],
)
def test_code_gen_aarch64(snapshot, program):
    snapshot.assert_match(
        code_gen(parse(program), Arch.aarch64), "out.asm"
    )


@pytest.mark.parametrize(
    "size,expected",
    [(0, 0), (1, 16), (15, 16), (16, 16), (31, 32), (33, 48)],
)
def test_stack_alignment(size, expected):
    assert stack_alignment(size) == expected

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
        pytest.param("let x = 1; { let y = 42; } exit(x);", id="block")
    ],
)
def test_code_gen_aarch64(snapshot, program):
    snapshot.assert_match(
        code_gen(parse(program), Arch.aarch64), "out.asm"
    )


@pytest.mark.parametrize(
    "size,expected",
    [
        (0, 0),
        (1, 16),
        (15, 16),
        (16, 16),
        (31, 32),
        (33, 48)
    ]
)
def test_stack_alignment(size, expected):
    assert stack_alignment(size) == expected

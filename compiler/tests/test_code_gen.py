import pytest
from compiler.arch import Arch
from compiler.code_gen import code_gen
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

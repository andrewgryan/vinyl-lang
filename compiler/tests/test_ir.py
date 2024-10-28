from compiler import ir, parser
import pytest


def test_visitor():
    ast = parser.parse(
        """
        let x = 3;
        exit(0);
    """
    )
    assert ir.visit(ast) == [
        ("=", "x", 3, None),
        ("exit", 0, None, None)
    ]


def gas(instructions):
    for (op, arg1, arg2, result) in instructions:
        if op == "=":
            yield f"mov ${arg2}, -0x8(%rbp)"
        elif op == "exit":
            yield f"mov $60, %rax"
            yield f"mov ${arg1}, %rdi"
            yield f"syscall"


def aarch64(instructions):
    for (op, arg1, arg2, result) in instructions:
        if op == "=":
            yield f"mov [sp, #0x8], #{hex(arg2)}"
        elif op == "exit":
            yield f"mov x8, #0x5d"
            yield f"mov x0, #{hex(arg1)}"
            yield f"svc 0"


def render(lines):
    return "\n".join(lines) + "\n"


def test_ir_code_gen():
    ir = [("=", "x", 3, None), ("exit", 0, None, None)]
    assert list(gas(ir)) == [
        "mov $3, -0x8(%rbp)",
        "mov $60, %rax",
        "mov $0, %rdi",
        "syscall",
    ]
    assert list(aarch64(ir)) == [
        "mov [sp, #0x8], #0x3",
        "mov x8, #0x5d",
        "mov x0, #0x0",
        "svc 0",
    ]

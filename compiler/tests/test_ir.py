from compiler import ir, parser
import pytest


def test_visitor():
    ast = parser.parse("""
        let x = 3;
        exit(0);
    """)
    assert list(ir.visit(ast)) == [
        ("program", "start", None, None),
        ("=", "x", 3, None),
        ("exit", 0, None, None),
        ("program", "end", None, None),
    ]


def test_visitor_main_program():
    ast = parser.parse("""
        fn main() {
            return 42;
        }
        main();
    """)
    assert list(ir.visit(ast)) == [
        ("program", "start", None, None),
        ("fn", "main", None, None),
        ("return", 42, None, None),
        ("call", "main", None, None),
        ("program", "end", None, None),
    ]


def test_ir_code_gen():
    instructions = [("=", "x", 3, None), ("exit", 0, None, None)]
    assert list(ir.gas(instructions)) == [
        "mov $3, -0x8(%rbp)",
        "mov $60, %rax",
        "mov $0, %rdi",
        "syscall",
    ]
    assert list(ir.aarch64(instructions)) == [
        "mov [sp, #0x8], #0x3",
        "mov x8, #0x5d",
        "mov x0, #0x0",
        "svc 0",
    ]

def test_ir_return():
    instructions = [("return", 42, None, None)]
    assert list(ir.aarch64(instructions)) == [
        "mov x0, #0x2a",
        "ret",
    ]
    assert list(ir.gas(instructions)) == [
        "mov $42, %rax",
        "ret",
    ]

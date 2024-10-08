from compiler.arch import Arch
from compiler.parser import NodeLet, NodeExit, NodeInt, NodeBlock


def code_gen(program, arch):
    if arch == Arch.aarch64:
        return code_gen_aaarch64(program)
    else:
        return code_gen_x86_64(program)


def code_gen_aaarch64(program):
    lines = [
        ".global _start",
        ".section .text",
        "",
        "_start:"
    ]
    lines += code_gen_statements(program.statements, stack_offset=8)
    return "\n".join(lines) + "\n"


def code_gen_block(block) -> list[str]:
    return code_gen_statements(block.statements)


def code_gen_statements(statements, stack_offset=0):
    lines = []
    # Stack allocate space for variables
    declarations = []
    for statement in statements:
        if isinstance(statement, NodeLet):
            declarations.append(statement.identifier.text)

    # Decrement stack pointer
    size_in_bytes = 8 * len(declarations)
    if size_in_bytes > 0:
        lines += [
            line("sub", "sp", "sp", f"#{hex(size_in_bytes + stack_offset)}")
        ]

    for statement in statements:
        if isinstance(statement, NodeExit):
            if isinstance(statement.status, NodeInt):
                code = int(statement.status.token.text)
                lines += [
                    line("mov", "x8", "#0x5d"),
                    line("mov", "x0", f"#{hex(code)}"),
                    line("svc", "0")
                ]
            else:
                index = declarations.index(
                    statement.status.token.text
                )
                offset = (index + 1) * 8
                lines += [
                    line("mov", "x8", "#0x5d"),
                    line("ldr", "x0", f"[sp, #{hex(offset)}]"),
                    line("svc", "0")
                ]
        elif isinstance(statement, NodeLet):
            index = declarations.index(statement.identifier.text)
            value = int(statement.value.text)
            offset = (index + 1) * 8
            lines += [
                line("mov", "w0", f"#{hex(value)}"),
                line("str", "w0", f"[sp, #{hex(offset)}]")
            ]
        elif isinstance(statement, NodeBlock):
            lines += code_gen_block(statement)

    # Restore stack pointer
    if size_in_bytes > 0:
        lines += [
            line("add", "sp", "sp", f"#{hex(size_in_bytes + stack_offset)}")
        ]
    return lines


def line(instruction, *args):
    return f"        {instruction} {', '.join(args)}"

def code_gen_x86_64(program):
    content = """
    .text
    .globl _start

_start:
"""
    # Stack allocate space for variables
    declarations = []
    for statement in program.statements:
        if isinstance(statement, NodeLet):
            declarations.append(statement.identifier.text)

    if len(declarations) > 0:
        content += f"""
        push  %rbp
        mov   %rsp, %rbp
        sub   ${8 * len(declarations)}, %rsp
"""

    # Exit statement(s)
    for statement in program.statements:
        if isinstance(statement, NodeExit):
            code = int(statement.status.token.text)
            content += f"""
        mov $60, %rax
        mov ${code}, %rdi
        syscall
"""
        elif isinstance(statement, NodeLet):
            index = declarations.index(statement.identifier.text)
            value = int(statement.value.text)
            content += f"""
        mov  ${index}, %rdi
        movq ${value}, (%rsp, %rdi, 8)
"""

    # Restore stack pointer
    if len(declarations) > 0:
        content += """
        mov  %rbp, %rsp
        pop  %rbp
"""
    return content

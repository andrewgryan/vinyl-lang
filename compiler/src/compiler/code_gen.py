from compiler.arch import Arch
from compiler.parser import NodeLet, NodeExit, NodeInt


def code_gen(program, arch):
    if arch == Arch.aarch64:
        return code_gen_aaarch64(program)
    else:
        return code_gen_x86_64(program)


def code_gen_aaarch64(program):
    content = """
.global _start
.section .text

_start:
"""
    # Stack allocate space for variables
    declarations = []
    for statement in program.statements:
        if isinstance(statement, NodeLet):
            declarations.append(statement.identifier.text)

    # Decrement stack pointer
    size_in_bytes = 8 * len(declarations)
    if size_in_bytes > 0:
        content += f"""
        sub sp, sp, #{hex(size_in_bytes + 8)}
"""

    for statement in program.statements:
        if isinstance(statement, NodeExit):
            if isinstance(statement.status, NodeInt):
                code = int(statement.status.token.text)
                content += f"""
        mov x8, #0x5d
        mov x0, #{hex(code)}
        svc 0
"""
            else:
                index = declarations.index(statement.status.token.text)
                offset = (index + 1) * 8
                content += f"""
        mov x8, #0x5d
        ldr x0, [sp, #{hex(offset)}]
        svc 0
"""
        elif isinstance(statement, NodeLet):
            index = declarations.index(statement.identifier.text)
            value = int(statement.value.text)
            offset = (index + 1) * 8
            content += f"""
        mov w0, #{hex(value)}
        str w0, [sp, #{hex(offset)}]
"""

    # Restore stack pointer
    if size_in_bytes > 0:
        content += f"""
        add sp, sp, #{hex(size_in_bytes + 8)}
"""
    return content


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


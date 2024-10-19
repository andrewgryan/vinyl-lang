from compiler.arch import Arch
from compiler.parser import (
    NodeBinOp,
    NodeLet,
    NodeExit,
    NodeInt,
    NodeBlock,
)
from compiler import parser




def code_gen(program, arch):
    if arch == Arch.aarch64:
        return code_gen_aaarch64(program)
    else:
        return code_gen_x86_64(program)


def stack_alignment(address: int):
    if address % 16 == 0:
        return address
    else:
        return ((address >> 4) + 1) << 4


def code_gen_aaarch64(ast):
    lines = [".global _start"]
    lines += data_section(ast)
    lines += [".section .text", "", "_start:"]
    lines += code_gen_statements(ast.statements)
    return "\n".join(lines) + "\n"


def data_section(ast, count=0):
    lines, _ = data_block(ast, count)
    if len(lines) > 0:
        lines = ["", ".data"] + lines + [""]
    return lines


def data_block(ast, count=0):
    lines = []
    for statement in ast.statements:
        if isinstance(statement, parser.NodeFunction):
            _lines, count = data_block(statement.body, count=count)
            lines += _lines
        if isinstance(statement, parser.NodePrint):
            lines += data_print(count, statement.message.token.text)
            count += 1
    return lines, count


def data_print(count, text):
    return [
        f"p{count}:",
        f"        .ascii \"{text}\\n\"",
        f"p{count}_len = . - p{count}",
    ]


def code_gen_block(block) -> list[str]:
    return code_gen_statements(block.statements)


def code_gen_statements(statements):
    lines = []
    # Stack allocate space for variables
    declarations = []
    for statement in statements:
        if isinstance(statement, NodeLet):
            declarations.append(statement.identifier.text)

    # Decrement stack pointer
    size_in_bytes = stack_alignment(8 * len(declarations))
    if size_in_bytes > 0:
        lines += [
            line(
                "sub",
                "sp",
                "sp",
                f"#{hex(size_in_bytes)}",
            )
        ]

    print_count = 0
    for statement in statements:
        if isinstance(statement, parser.NodeFunction):
            lines += visit_function(statement)
        if isinstance(statement, parser.NodePrint):
            lines += visit_print(statement, print_count)
            print_count += 1
        elif isinstance(statement, NodeExit):
            if isinstance(statement.status, NodeInt):
                code = int(statement.status.token.text)
                lines += [
                    line("mov", "x8", "#0x5d"),
                    line("mov", "x0", f"#{hex(code)}"),
                    line("svc", "0"),
                ]
            elif isinstance(statement.status, NodeBinOp):
                # Recursively evaluate binary operations
                lines += visit_bin(statement.status)
                lines += [
                    line("mov", "x8", "#0x5d"),
                    line("mov", "x0", "x1"),
                    line("svc", "0"),
                ]
            else:
                index = declarations.index(
                    statement.status.token.text
                )
                offset = (index + 1) * 8
                lines += [
                    line("mov", "x8", "#0x5d"),
                    line("ldr", "x0", f"[sp, #{hex(offset)}]"),
                    line("svc", "0"),
                ]
        elif isinstance(statement, NodeLet):
            # Calculate value or expression
            if isinstance(statement.value, NodeInt):
                value = int(statement.value.token.text)
                lines += [
                    line("mov", "x1", f"#{hex(value)}"),
                ]
            elif isinstance(statement.value, NodeBinOp):
                lines += visit_bin(statement.value)

            # Store value on stack
            index = declarations.index(statement.identifier.text)
            offset = (index + 1) * 8
            lines += [
                line("str", "x1", f"[sp, #{hex(offset)}]"),
            ]
        elif isinstance(statement, NodeBlock):
            lines += code_gen_block(statement)

    # Restore stack pointer
    if size_in_bytes > 0:
        lines += [
            line(
                "add",
                "sp",
                "sp",
                f"#{hex(size_in_bytes)}",
            )
        ]
    return lines


def visit_print(statement: parser.NodePrint, count: int):
    return [
            line("mov", "x8", "#0x40"),  # write
            line("mov", "x0", "#0x1"),  # stdout
            line("ldr", "x1", f"=p{count}"),  # chars
            line("ldr", "x2", f"=p{count}_len"),  # length
            line("svc", "0"),
        ]


def visit_function(fn):
    return [f"{fn.identifier.token.text}:"] + code_gen_block(
        fn.body
    )


def visit_bin(node):
    if isinstance(node.lhs, NodeBinOp):
        cmd = {"+": "add", "-": "sub"}[node.operator.operator]
        rhs = int(node.rhs.token.text)
        return visit_bin(node.lhs) + [
            line("mov", "x0", f"#{hex(rhs)}"),
            line(cmd, "x1", "x1", "x0"),
        ]
    else:
        lhs = int(node.lhs.token.text)
        rhs = int(node.rhs.token.text)
        cmd = {"+": "add", "-": "sub"}[node.operator.operator]
        return [
            line("mov", "x1", f"#{hex(lhs)}"),
            line("mov", "x0", f"#{hex(rhs)}"),
            line(cmd, "x1", "x1", "x0"),
        ]


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
            value = int(statement.value.token.text)
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

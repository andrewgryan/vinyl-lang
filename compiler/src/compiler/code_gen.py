from compiler.arch import Arch
from compiler.parser import (
    NodeBinOp,
    NodeLet,
    NodeExit,
    NodeInt,
    NodeBlock,
)
from compiler import parser, x86_64


def gas(instructions):
    return render(gas_lines(instructions))


def gas_lines(instructions):
    for op, arg1, arg2, result in instructions:
        if (op, arg1) == ("global", "start"):
            yield ".global _start"
        elif (op, arg1) == ("section", "text"):
            yield ".text"
        elif op == "label":
            yield f"{arg1}:"
        elif op == "=":
            yield f"mov ${arg2}, -0x8(%rbp)"
        elif op == "exit":
            yield f"mov $60, %rax"
            yield f"mov ${arg1}, %rdi"
            yield f"syscall"
        elif op == "return":
            yield f"mov ${arg1}, %rax"
        elif op == "call":
            yield f"call {arg1}"
        elif op == "ret":
            yield f"ret"


def aarch64(instructions):
    return render(aarch64_lines(instructions))


def aarch64_lines(instructions):
    for op, arg1, arg2, result in instructions:
        if op == "=":
            yield f"mov [sp, #0x8], #{hex(arg2)}"
        elif op == "exit":
            yield f"mov x8, #0x5d"
            yield f"mov x0, #{hex(arg1)}"
            yield f"svc 0"
        elif op == "return":
            yield f"mov x0, #{hex(arg1)}"
            yield f"ret"
        elif (op, arg1) == ("global", "start"):
            yield ".global _start"
        elif (op, arg1) == ("section", "text"):
            yield ".section .text"
        elif op == "label":
            yield f"{arg1}:"
        elif op == "call":
            yield f"bl {arg1}"
        elif op == "ret":
            yield f"ret"


def render(lines):
    return "\n".join(lines) + "\n"


# DEPRECATE


def code_gen(program, arch):
    if arch == Arch.aarch64:
        return code_gen_aaarch64(program)
    else:
        return x86_64.code_gen_x86_64(program)


def stack_alignment(address: int):
    if address % 16 == 0:
        return address
    else:
        return ((address >> 4) + 1) << 4


def code_gen_aaarch64(ast):
    lines = [".global _start"]
    lines += data_section(ast)
    lines += [".section .text", ""]
    lines += code_gen_functions(ast)
    lines += ["_start:"]
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
            _lines, count = data_block(
                statement.body, count=count
            )
            lines += _lines
        if isinstance(statement, parser.NodePrint):
            lines += data_print(
                count, statement.message.token.text
            )
            count += 1
    return lines, count


def data_print(count, text):
    return [
        f"p{count}:",
        f'        .ascii "{text}\\n"',
        f"p{count}_len = . - p{count}",
    ]


def code_gen_block(block) -> list[str]:
    return code_gen_statements(block.statements)


def code_gen_functions(ast):
    lines = []
    for statement in ast.statements:
        if isinstance(statement, parser.NodeFunction):
            lines += visit_function(statement)
    return lines


def code_gen_statements(statements):
    lines = []
    # Stack allocate space for variables
    declarations = []
    for statement in statements:
        if isinstance(statement, NodeLet):
            declarations.append(statement.identifier.token.text)

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
        if isinstance(statement, parser.NodeCall):
            lines += visit_call(statement)
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
            index = declarations.index(
                statement.identifier.token.text
            )
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


def visit_call(statement: parser.NodeCall):
    return [line("bl", statement.identifier.token.text)]


def visit_print(statement: parser.NodePrint, count: int):
    return [
        line("mov", "x8", "#0x40"),  # write
        line("mov", "x0", "#0x1"),  # stdout
        line("ldr", "x1", f"=p{count}"),  # chars
        line("ldr", "x2", f"=p{count}_len"),  # length
        line("svc", "0"),
    ]


def visit_function(fn):
    return (
        [f"{fn.identifier.token.text}:"]
        + code_gen_block(fn.body)
        + ["ret", ""]
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

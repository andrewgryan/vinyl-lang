import subprocess
from dataclasses import dataclass
from enum import Enum
from compiler.lexer import lex, Token, TokenKind


@dataclass
class NodeInt:
    token: Token


@dataclass
class NodeIdentifier:
    token: Token


@dataclass
class NodeExit:
    status: NodeInt | NodeIdentifier


@dataclass
class NodeLet:
    identifier: Token
    value: Token


@dataclass
class NodeProgram:
    statements: list[NodeExit]


def parse(content: str):
    tokens = list(lex(content))
    for token in tokens:
        print(token)
    cursor = 0
    statements = []
    while cursor < len(tokens):
        statement, cursor = parse_exit(tokens, cursor)
        if statement:
            statements.append(statement)
            continue
        statement, cursor = parse_let(tokens, cursor)
        if statement:
            statements.append(statement)
            continue
        else:
            cursor += 1
    return NodeProgram(statements)


def exit(status: str):
    return NodeExit(NodeInt(Token.int(status)))


def parse_exit(tokens, cursor):
    if ((tokens[cursor + 0].kind == TokenKind.EXIT) and
        (tokens[cursor + 1].kind == TokenKind.LEFT_PAREN) and
        (tokens[cursor + 3].kind == TokenKind.RIGHT_PAREN) and
        (tokens[cursor + 4].kind == TokenKind.SEMICOLON)):
        status, cursor = parse_expression(tokens, cursor + 2)
        return NodeExit(status=status), cursor + 2
    else:
        return None, cursor

def let(identifier: str, value: str):
    return NodeLet(Token.identifier(identifier), Token.int(value))

def parse_let(tokens, cursor):
    rule = (
        TokenKind.LET,
        TokenKind.IDENTIFIER,
        TokenKind.EQUAL,
        TokenKind.INT,
        TokenKind.SEMICOLON,
    )
    kinds = tuple(
        token.kind for token in tokens[cursor : cursor + 5]
    )
    if rule == kinds:
        node = NodeLet(tokens[cursor + 1], tokens[cursor + 3])
        return node, cursor + 5
    else:
        return None, cursor


def parse_expression(tokens, cursor):
    if tokens[cursor].kind == TokenKind.INT:
        return NodeInt(tokens[cursor]), cursor + 1
    elif tokens[cursor].kind == TokenKind.IDENTIFIER:
        return NodeIdentifier(tokens[cursor]), cursor + 1
    else:
        return None, cursor


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
        print(statement)
        if isinstance(statement, NodeExit):
            if isinstance(statement.status, NodeInt):
                code = int(statement.status.token.text)
                content += f"""
        mov x8, #0x5d
        mov x0, #{hex(code)}
        svc 0
"""
            else:
                content += f"""
        mov x8, #0x5d
        ldr x0, [sp, #{hex(8)}]
        svc 0
"""
        elif isinstance(statement, NodeLet):
            index = declarations.index(statement.identifier.text)
            value = int(statement.value.text)
            offset = size_in_bytes
            content += f"""
        mov     w0, #{hex(value)}
        str     w0, [sp, #{hex(offset)}]
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


class Arch(str, Enum):
    x86_64 = "x86_64"
    aarch64 = "aarch64"


def main(
    src: str, arch: Arch = Arch.aarch64, gcc_version: int = 11
):
    print(f"compiling: {src}")
    with open(src, "r") as stream:
        content = stream.read()

    # Convert vinyl to assembly
    ast = parse(content)

    content = code_gen(ast, arch)
    with open("vinyl.asm", "w") as stream:
        stream.write(content)

    # Compile
    command = [
        f"{arch.value}-linux-gnu-as",
        "vinyl.asm",
        "-o",
        "vinyl.o",
    ]
    subprocess.check_call(command)

    # Link
    command = [
        f"{arch.value}-linux-gnu-gcc-{gcc_version}",
        "vinyl.o",
        "-o",
        "vinyl.exe",
        "-nostdlib",
        "-static",
    ]
    subprocess.check_call(command)

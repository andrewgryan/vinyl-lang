import subprocess
from dataclasses import dataclass
from enum import Enum


class TokenKind(Enum):
    COMMENT = 1
    LEFT_PAREN = 2
    RIGHT_PAREN = 3
    SEMICOLON = 4
    EXIT = 5
    INT = 6
    LET = 7
    EQUAL = 8
    IDENTIFIER = 9


@dataclass
class Token:
    kind: TokenKind
    text: str

def lex_comment(cursor, content):
    begin = cursor
    while (cursor < len(content)):
        if content[cursor] == "\n":
            break
        cursor += 1
    token = Token(
        kind = TokenKind.COMMENT,
        text = content[begin:cursor + 1]
    )
    return cursor + 1, token

def lex_int(cursor, content):
    begin = cursor
    while (cursor < len(content)):
        if content[cursor].isdigit():
            cursor += 1
        else:
            break
    token = Token(
        kind = TokenKind.INT,
        text = content[begin:cursor]
    )
    return cursor, token

def lex_identifier(cursor, content):
    begin = cursor

    # First char [a-zA-Z]
    if not content[begin].isalpha():
        return cursor, None
    
    # All other chars [a-zA-Z0-9]
    while (cursor < len(content)):
        if content[cursor].isalnum():
            cursor += 1
        else:
            break

    token = Token(
        kind = TokenKind.IDENTIFIER,
        text = content[begin:cursor]
    )
    return cursor, token

def lex_exit(cursor, content):
    token = Token(
        kind = TokenKind.EXIT,
        text = content[cursor:cursor + 4]
    )
    return cursor + 4, token

def lex_let(cursor, content):
    length = len("let")
    token = Token(
        kind = TokenKind.LET,
        text = content[cursor:cursor + length]
    )
    return cursor + length, token


def lex(content):
    cursor = 0
    while (cursor < len(content)):
        if content[cursor] == "#":
            cursor, token = lex_comment(cursor, content)
            yield token
        elif content[cursor].isdigit():
            cursor, token = lex_int(cursor, content)
            yield token
        elif content[cursor:cursor + 4] == "exit":
            cursor, token = lex_exit(cursor, content)
            yield token
        elif content[cursor:].startswith("let"):
            cursor, token = lex_let(cursor, content)
            yield token
        elif content[cursor].isalpha():
            cursor, token = lex_identifier(cursor, content)
            yield token
        elif content[cursor] == "=":
            token = Token(
                kind=TokenKind.EQUAL,
                text="="
            )
            yield token
            cursor += 1
        elif content[cursor] == "(":
            token = Token(
                kind=TokenKind.LEFT_PAREN,
                text="("
            )
            yield token
            cursor += 1
        elif content[cursor] == ")":
            token = Token(
                kind=TokenKind.RIGHT_PAREN,
                text=")"
            )
            yield token
            cursor += 1
        elif content[cursor] == ";":
            token = Token(
                kind=TokenKind.SEMICOLON,
                text=";"
            )
            yield token
            cursor += 1
        else:
            cursor += 1

@dataclass
class NodeInt:
    token: Token

@dataclass
class NodeExit:
    status: NodeInt

@dataclass
class NodeProgram:
    statements: list[NodeExit]


def parse(content: str):
    tokens = list(lex(content))
    for token in tokens:
        print(token)
    cursor = 0
    statements = []
    while (cursor < len(tokens)):
        statement, cursor = parse_exit(tokens, cursor)
        if statement:
            statements.append(statement)
        else:
            cursor += 1
    return NodeProgram(statements)


def parse_exit(tokens, cursor):
    rule = (
        TokenKind.EXIT,
        TokenKind.LEFT_PAREN,
        TokenKind.INT,
        TokenKind.RIGHT_PAREN,
        TokenKind.SEMICOLON,
    )
    if all(tokens[cursor + i].kind == kind
           for i, kind in enumerate(rule)):
        status, _ = parse_expression(tokens, cursor + 2)
        return NodeExit(status=status), cursor + len(rule)
    else:
        return None, cursor


def parse_expression(tokens, cursor):
    if tokens[cursor].kind == TokenKind.INT:
        return NodeInt(tokens[cursor]), cursor + 1
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
    for statement in program.statements:
        code = int(statement.status.token.text)
        content += f"""
        mov x8, #0x5d
        mov x0, #{hex(code)}
        svc 0
"""
    return content


def code_gen_x86_64(program):
    content = """
    .text
    .globl _start

_start:
"""
    for statement in program.statements:
        code = int(statement.status.token.text)
        content += f"""
        mov $60, %rax
        mov ${code}, %rdi
        syscall
"""
    return content


class Arch(str, Enum):
    x86_64 = "x86_64"
    aarch64 = "aarch64"


def main(src: str, arch: Arch = Arch.aarch64, gcc_version: int = 11):
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
       "vinyl.o"
    ]
    subprocess.check_call(command)

    # Link
    command = [
        f"{arch.value}-linux-gnu-gcc-{gcc_version}",
        "vinyl.o",
        "-o",
        "vinyl.exe",
        "-nostdlib",
        "-static"
    ]
    subprocess.check_call(command)

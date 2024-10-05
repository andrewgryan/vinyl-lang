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


def lex_exit(cursor, content):
    token = Token(
        kind = TokenKind.EXIT,
        text = content[begin:cursor + 4]
    )
    return cursor + 4, token


def lex(content):
    cursor = 0
    while (cursor < len(content)):
        if content[cursor] == "#":
            cursor, token = lex_comment(cursor, content)
            print(token)
        elif content[cursor:cursor + 4] == "exit":
            cursor, token = lex_exit(cursor, content)
            print(token)
        else:
            cursor += 1

def parse(content: str):
    # TODO: Lex, parse
    tokens = lex(content)
    return 42

def main(src: str):
    print(f"compiling: {src}")
    with open(src, "r") as stream:
        content = stream.read()

    code = parse(content)

    # TODO: code gen
    content = f"""
.global _start
.section .text

_start:
        mov x8, #0x5d
        mov x0, #{hex(code)}
        svc 0
"""
    with open("vinyl.asm", "w") as stream:
        stream.write(content)
    # TODO: Compile and link asm
    command = [
    "aarch64-linux-gnu-as",
     "vinyl.asm",
      "-o",
       "vinyl.o"
    ]
    subprocess.call(command)
    command = [
        "aarch64-linux-gnu-gcc-11",
        "vinyl.o",
        "-o",
        "vinyl.exe",
        "-nostdlib",
        "-static"
    ]
    subprocess.call(command)

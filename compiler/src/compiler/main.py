import subprocess
from compiler.arch import Arch
from compiler.parser import parse
from compiler import analyser, ir, code_gen


def main(
    src: str,
    arch: Arch = Arch.aarch64,
    gcc_version: int = 11,
    dry_run: bool = False,
):
    print(f"compiling: {src}")
    with open(src, "r") as stream:
        content = stream.read()

    # Convert vinyl to assembly
    ast = parse(content)

    ast = analyser.analyse(ast)

    instructions = ir.visit(ast)
    if arch == Arch.aarch64:
        code = code_gen.aarch64(instructions)
    else:
        code = code_gen.gas(instructions)

    if dry_run:
        print(code)
        return

    # content = code_gen(ast, arch)
    with open("vinyl.asm", "w") as stream:
        stream.write(code)

    # Compile
    command = [
        f"{arch.value}-linux-gnu-as",
        "vinyl.asm",
        "-o",
        "vinyl.o",
        "-g"
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

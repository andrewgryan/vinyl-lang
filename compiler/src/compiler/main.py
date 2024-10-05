import subprocess
def main(src: str):
    print(f"compiling: {src}")
    # TODO: Lex, parse and code gen
    content = """
.global _start
.section .text

_start:
        mov x8, #0x5d
        mov x0, #0x41
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

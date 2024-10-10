
.global _start
.section .text

_start:

        sub sp, sp, #0x10

        mov w0, #0x2a
        str w0, [sp, #0x8]

        add sp, sp, #0x10

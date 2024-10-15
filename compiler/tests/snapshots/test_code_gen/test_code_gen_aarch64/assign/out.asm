.global _start
.section .text

_start:
        sub sp, sp, #0x10
        mov x1, #0x2a
        str x1, [sp, #0x8]
        add sp, sp, #0x10

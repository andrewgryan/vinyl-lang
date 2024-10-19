.global _start
.section .text

foo:
        sub sp, sp, #0x10
        mov x1, #0x1
        str x1, [sp, #0x8]
        add sp, sp, #0x10

_start:

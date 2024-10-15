.global _start
.section .text

_start:
        mov x1, #0x3
        mov x0, #0x1
        sub x1, x1, x0
        mov x8, #0x5d
        mov x0, x1
        svc 0

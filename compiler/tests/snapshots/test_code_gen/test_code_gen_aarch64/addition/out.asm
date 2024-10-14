.global _start
.section .text

_start:
        mov x0, #0x1
        mov x1, #0x2
        add x1, x1, x0
        mov x8, #0x5d
        mov x0, x1
        svc 0

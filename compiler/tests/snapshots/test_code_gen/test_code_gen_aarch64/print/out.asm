.global _start
.section .text

_start:
        mov x8, #0x40
        mov x0, #0x1
        mov x1, #0x40
        mov x2, #0x1
        svc 0

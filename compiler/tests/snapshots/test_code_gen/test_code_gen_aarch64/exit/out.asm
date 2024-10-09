
.global _start
.section .text

_start:

        mov x8, #0x5d
        mov x0, #0x2a
        svc 0

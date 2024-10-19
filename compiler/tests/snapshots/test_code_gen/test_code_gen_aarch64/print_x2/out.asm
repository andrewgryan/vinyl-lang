.global _start

.data
p0:
        .ascii "42\n"
p0_len = . - p0
p1:
        .ascii "7\n"
p1_len = . - p1

.section .text

_start:
        mov x8, #0x40
        mov x0, #0x1
        ldr x1, =p0
        ldr x2, =p0_len
        svc 0
        mov x8, #0x40
        mov x0, #0x1
        ldr x1, =p1
        ldr x2, =p1_len
        svc 0

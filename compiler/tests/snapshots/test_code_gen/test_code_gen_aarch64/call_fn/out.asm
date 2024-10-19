.global _start

.data
p0:
        .ascii "42\n"
p0_len = . - p0

.section .text

foo:
        mov x8, #0x40
        mov x0, #0x1
        ldr x1, =p0
        ldr x2, =p0_len
        svc 0
ret

_start:
        bl foo

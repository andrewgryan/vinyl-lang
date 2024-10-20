.global _start

.data
p0:
        .ascii "x\n"
p0_len = . - p0

.section .text

_start:
        sub sp, sp, #0x10
        mov x1, #0x4
        str x1, [sp, #0x8]
        mov x8, #0x40
        mov x0, #0x1
        ldr x1, =p0
        ldr x2, =p0_len
        svc 0
        add sp, sp, #0x10

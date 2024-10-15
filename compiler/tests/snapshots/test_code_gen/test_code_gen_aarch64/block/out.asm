.global _start
.section .text

_start:
        sub sp, sp, #0x10
        mov x1, #0x1
        str x1, [sp, #0x8]
        sub sp, sp, #0x10
        mov x1, #0x2a
        str x1, [sp, #0x8]
        add sp, sp, #0x10
        mov x8, #0x5d
        ldr x0, [sp, #0x8]
        svc 0
        add sp, sp, #0x10

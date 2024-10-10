
.global _start
.section .text

_start:

        sub sp, sp, #0x18

        mov w0, #0x2a
        str w0, [sp, #0x8]

        mov w0, #0x7
        str w0, [sp, #0x10]

        mov x8, #0x5d
        ldr x0, [sp, #0x8]
        svc 0

        add sp, sp, #0x18

.global _start
.section .text

_start:
        # Stack allocate
        sub sp, sp, #0x10
        mov w0, #42
        str w0, [sp, #12]

        # Write
        mov x8, #64
        mov x0, #1
        ldr x1, =message
        mov x2, #13
        svc 0

        # Exit
        mov x8, #0x5d
        ldr w0, [sp, #12]
        svc 0

        add sp, sp, #0x10

.section .data
        message:
        .ascii "Hello, World\n"

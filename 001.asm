.global _start
.section .text

_start:
        # Write
        mov x8, #64
        mov x0, #1
        ldr x1, =message
        mov x2, #13
        svc 0

        # Exit
        mov x8, #0x5d
        mov x0, #0x41
        svc 0

.section .data
        message:
        .ascii "Hello, World\n"

.global _start

.data
msg:
        .ascii "42\n"
msg_len = . - msg

.section .text

_start:
        mov x8, #0x40
        mov x0, #0x1
        ldr x1, =msg
        ldr x2, =msg_len
        svc 0

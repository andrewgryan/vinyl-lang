        .global _start
        .data
msg: .ascii "Hello, World!\n"
msg_len = (. - msg)

        .text

_start:
        # System write
        mov        $1, %rax
        mov        $1, %rdi
        mov        $msg, %rsi
        mov        $msg_len, %rdx
        syscall

        # System exit
        mov        $60, %rax
        mov        $1, %rdi
        syscall

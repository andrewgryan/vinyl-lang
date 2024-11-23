        .global _start
        .data
msg: .ascii "Hello, World!\n"
msg_len = (. - msg)

in_name: .asciz "data.txt"
in_name_len = (. - in_name)
out_name: .asciz "out.txt"
out_name_len = (. - out_name)

SYS_WRITE = 1
SYS_OPEN = 2
SYS_CLOSE = 3

O_CREAT = 0x40
O_RDONLY = 0x0
O_WRONLY = 0x1
O_RDWR = 0x2


        .text
_start:
        # Open output file create mode
        mov        $SYS_OPEN, %rax
        mov        $out_name, %rdi
        mov        $(O_WRONLY | O_CREAT), %rsi
        mov        $0666, %rdx
        syscall

        # Save file handle
        mov        %rax, %r9

        # System write
        mov        $SYS_WRITE, %rax
        mov        %r9, %rdi
        mov        $msg, %rsi
        mov        $msg_len, %rdx
        syscall

        # Open input in read mode
        mov        $SYS_OPEN, %rax
        mov        $in_name, %rdi
        mov        $O_RDONLY, %rsi
        syscall

        # Save input file handle
        mov        %rax, %r8

        # Close input file
        mov        $SYS_CLOSE, %rax
        mov        %r8, %rdi
        syscall

        # Close output file
        mov        $SYS_CLOSE, %rax
        mov        %r9, %rdi
        syscall

        # System exit
        mov        $60, %rax
        mov        %r9, %rdi
        syscall

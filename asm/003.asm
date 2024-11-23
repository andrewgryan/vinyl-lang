        .global _start
        .data
msg: .ascii "Hello, World!\n"
msg_len = (. - msg)

buf: .space 1024, 0
buf_len = 1024

in_name: .asciz "in.txt"
in_name_len = (. - in_name)
out_name: .asciz "out.txt"
out_name_len = (. - out_name)

STDOUT = 0

SYS_READ = 0
SYS_WRITE = 1
SYS_OPEN = 2
SYS_CLOSE = 3

O_CREAT = 0x40
O_RDONLY = 0x0
O_WRONLY = 0x1
O_RDWR = 0x2

fd_in: .quad 0
fd_out: .quad 0
bytes: .quad 0

        .text

clear:
        xor        %rax, %rax
        mov        $buf, %rdi
        jmp        .L1
.L1:
        movb       $0, 0(%rdi, %rax, 1)
        add        $1, %rax
        cmp        $buf_len, %rax
        jl         .L1
        ret

_start:
        # Open output file create mode
        mov        $SYS_OPEN, %rax
        mov        $out_name, %rdi
        mov        $(O_WRONLY | O_CREAT), %rsi
        mov        $0666, %rdx
        syscall
        mov        %rax, (fd_out)

        # Open input in read mode
        mov        $SYS_OPEN, %rax
        mov        $in_name, %rdi
        mov        $O_RDONLY, %rsi
        syscall
        mov        %rax, (fd_in)

.R1:
        # Read
        mov        $SYS_READ, %rax
        mov        (fd_in), %rdi
        mov        $buf, %rsi
        mov        $buf_len, %rdx
        syscall
        mov        %rax, (bytes)

        # System write
        mov        $SYS_WRITE, %rax
        mov        (fd_out), %rdi
        mov        $buf, %rsi
        mov        (bytes), %rdx
        syscall

        # Print
        mov        $SYS_WRITE, %rax
        mov        $STDOUT, %rdi
        mov        $buf, %rsi
        mov        (bytes), %rdx
        syscall

        cmp        $0, (bytes)
        jg         .R1

        # Close input file
        mov        $SYS_CLOSE, %rax
        mov        (fd_in), %rdi
        syscall

        # Close output file
        mov        $SYS_CLOSE, %rax
        mov        (fd_out), %rdi
        syscall

        # System exit
        mov        $60, %rax
        mov        $0, %rdi
        syscall

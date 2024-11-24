.include "sys.asm"

        .global _start
        .data

buf: .space 1024, 0
buf_len = 1024

in_name: .asciz "in.txt"
in_name_len = (. - in_name)
out_name: .asciz "out.txt"
out_name_len = (. - out_name)

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
        mov        $out_name, %rdi
        mov        $(O_WRONLY | O_CREAT), %rsi
        mov        $0666, %rdx
        call       open
        mov        %rax, (fd_out)

        # Open input in read mode
        mov        $in_name, %rdi
        mov        $O_RDONLY, %rsi
        call       open
        mov        %rax, (fd_in)

.R1:
        # Read
        mov        (fd_in), %rdi
        mov        $buf, %rsi
        mov        $buf_len, %rdx
        call       read
        mov        %rax, (bytes)

        # Write
        mov        (fd_out), %rdi
        mov        $buf, %rsi
        mov        (bytes), %rdx
        call       write

        # Print
        mov        $buf, %rdi
        mov        (bytes), %rsi
        call       print

        cmp        $0, (bytes)
        jg         .R1

        # Close input file
        mov        (fd_in), %rdi
        call       close

        # Close output file
        mov        (fd_out), %rdi
        call       close

        # System exit
        mov        $0, %rdi
        call       exit

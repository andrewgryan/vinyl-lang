        .global _start
        .text

foo:
        push       %rbp
        mov        %rsp, %rbp
        mov        $7, %rax
        mov        %rbp, %rsp
        pop        %rbp
        ret

_start:
        call       foo

        mov        $60, %rax
        mov        $1, %rdi
        syscall

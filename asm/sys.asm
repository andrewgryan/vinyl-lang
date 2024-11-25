
.data
STDOUT = 0

SYS_READ = 0
SYS_WRITE = 1
SYS_OPEN = 2
SYS_CLOSE = 3
SYS_EXIT = 60

O_CREAT = 0x40
O_RDONLY = 0x0
O_WRONLY = 0x1
O_RDWR = 0x2

.text
.global print
.global close
.global exit
.global read
.global write

/*
 *  Print statement
 *
 *  %rdi - address of buffer
 *  %rsi - length
 */
print:
        push       %rsi
        push       %rdi
        mov        $SYS_WRITE, %rax
        mov        $STDOUT, %rdi
        pop        %rsi        # %rdi from caller
        pop        %rdx        # %rsi from caller
        syscall
        ret


/**
 *  Close file handle
 *
 *  %rdi - file handle
 */
close:
        mov        $SYS_CLOSE, %rax
        syscall
        ret


/**
 *  Exit
 *
 *  %rdi - exit code (0-255)
 */
exit:
        mov        $SYS_EXIT, %rax
        syscall
        ret


/**
 *  Open
 *
 *  %rdi - file name string address
 *  %rsi - flags
 *  %rdx - mode
 */
open:
        mov        $SYS_OPEN, %rax
        syscall
        ret


/**
 *  Read
 *
 *  %rdi - file handle
 *  %rsi - buffer address
 *  %rdx - number of bytes to read
 */
read:
        mov        $SYS_READ, %rax
        syscall
        ret


/**
 *  Write
 *
 *  %rdi - file handle
 *  %rsi - buffer address
 *  %rdx - number of bytes to write
 */
write:
        mov        $SYS_WRITE, %rax
        syscall
        ret

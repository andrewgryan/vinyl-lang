.include "sys.asm"
.global _start
.text

/**
 *	ASCII to Int
 */
atoi:
	mov		%rdi, %rax
	sub	    $48, %rax
	cmp		$9, %rax
	jg		atoi_L1
	cmp		$0, %rax
	jl		atoi_L1
	ret
atoi_L1:
	mov		$-1, %rax
	ret

_start:
	mov		$46, %rdi
	call	atoi
	mov		%rax, %rdi
	call	exit

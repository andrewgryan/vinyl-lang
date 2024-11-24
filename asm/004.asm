.include "sys.asm"
.global _start

.data
	number: .ascii "123"
	number_len = (. - number)

.text


/**
 *  ASCII string to integer
 *
 *  %rdi - buffer address
 *  %rsi - buffer length
 */
atoi:
	# TODO: Use stack to preserve local variable
	xor		%rax, %rax
	xor		%rcx, %rcx
	mov		%rdi, %r8
	xor		%r9, %r9
	jmp		atoi_L2
atoi_L1:
	movzb	(%r8, %rcx, 1), %rdi
	mov		%r9, %rax
	mov		$10, %r10d
	mul		%r10d
	mov		%rax, %r9
	call	atod
	add		%rax, %r9
	inc		%rcx
atoi_L2:
	cmp		%rsi, %rcx
	jl		atoi_L1
	mov		%r9, %rax
	ret


/**
 *	ASCII to digit [0-9]
 */
atod:
	mov		%rdi, %rax
	sub	    $48, %rax
	cmp		$9, %rax
	jg		atod_L1
	cmp		$0, %rax
	jl		atod_L1
	ret
atod_L1:
	mov		$-1, %rax
	ret

_start:
	mov		$number, %rdi
	mov		$number_len, %rsi
	call	atoi
	mov		%rax, %rdi
	call	exit

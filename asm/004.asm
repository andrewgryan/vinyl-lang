.global _start

.data
	number: .ascii "42"
	number_len = (. - number)

.text
_start:
	mov		$number, %rdi
	mov		$number_len, %rsi
	call	print

	mov		$number, %rdi
	mov		$number_len, %rsi
	call	atoi

	mov		%rax, %rdi
	call	exit

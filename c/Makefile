all: hello dump

hello: hello.o
	aarch64-linux-gnu-gcc hello.o -o hello

hello.o: hello.c
	aarch64-linux-gnu-gcc -c hello.c

dump: hello.o
	aarch64-linux-gnu-objdump -d hello.o

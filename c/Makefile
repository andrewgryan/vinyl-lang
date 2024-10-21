all: hello dump

target = aarch64

hello: hello.o
	$(target)-linux-gnu-gcc hello.o -o hello

hello.o: hello.c
	$(target)-linux-gnu-gcc -c hello.c

dump: hello.o
	$(target)-linux-gnu-objdump -d hello.o

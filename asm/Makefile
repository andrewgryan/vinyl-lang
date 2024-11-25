number = 001
$(number): $(number).o sys.o ascii.o
	x86_64-linux-gnu-ld -o $(number) $(number).o sys.o ascii.o

$(number).o: $(number).asm
	x86_64-linux-gnu-as -g -o $(number).o $(number).asm

sys.o: sys.asm sys.asm
	x86_64-linux-gnu-as -g -o sys.o sys.asm

ascii.o: ascii.asm ascii.asm
	x86_64-linux-gnu-as -g -o ascii.o ascii.asm

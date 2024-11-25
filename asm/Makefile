number = 001
$(number): $(number).o sys.o
	x86_64-linux-gnu-ld -o $(number) $(number).o sys.o

$(number).o: $(number).asm
	x86_64-linux-gnu-as -g -o $(number).o $(number).asm

sys.o: sys.asm sys.asm
	x86_64-linux-gnu-as -g -o sys.o sys.asm

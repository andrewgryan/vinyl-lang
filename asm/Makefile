number = 001
$(number): $(number).o
	x86_64-linux-gnu-ld -o $(number) $(number).o

$(number).o: $(number).asm
	x86_64-linux-gnu-as -g -o $(number).o $(number).asm

TOOL    :=  loongarch32r-linux-gnusf-
CC      :=  $(TOOL)gcc
OBJCOPY :=  $(TOOL)objcopy
OBJDUMP :=  $(TOOL)objdump
QEMU    :=  qemu-system-loongarch32

.PHONY: clean qemu

start.elf: start.S main.c lab0.ld
	$(CC) -nostdlib -T lab0.ld start.S main.c -O3 -o $@

qemu: start.elf
	$(QEMU) -M ls3a5k32 -m 32M -kernel start.elf -nographic

clean:
	rm start.elf

# Umazing Emulator (VERY WIP)
An emulator for a dumb homebrew RISC CPU I made cause I got bored one night. Some parts are loosely based on the 6502 instruction set.

## Instruction Set
### Register A
- `ADDA` - Increment a
- `SUBA` - Decrement a
- `AWTA, A` - Write register A to RAM
- `BEA, A` - If register A is equal to the first operand, set program counter to the second operand 
- `RDAA, A` - Set register A to PC (incomplete in emulator)

### Register X
- `ADDX` - Increment x
- `SUBX` - Decrement x
- `AWTA, A` - Write register A to RAM
- `RDAX, A` - Set register x to PC (incomplete in emulator)

### Misc
- `AWXX` - Writes Register X to RAM address (Register A)
- `HLT` - Shutdown signal (halt CPU)
- `UPD` - Dump VRAM buffer
- `JMP, A` - Sets program counter to operand.

# Emulator info
The emulator built into this system roughly has these specifications
- 128 Bytes of RAM
- 16 Bytes of vRAM (Each startup sets these values to 0x20)
- The system bus layout is `RAM -> vRAM -> ROM`


### Note nmk bjhu7i86
I made everything except except for `uasm.py` which is entirely vibecoded cause my brain is too smooth to understand compilers (a crime against humanity cause i really fucking hate relying on chatbots to do my homework)
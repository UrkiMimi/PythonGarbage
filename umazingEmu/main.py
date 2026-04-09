import emu

#program = [0x87, 104, 0x82, 129, 0x87, 105, 0x82, 130, 0x85, 0x84]


emu.ALU.eROM = emu.Ru.importBytes('shitter2.bin')

emu.Ru.run()

print(emu.ALU.eRAM)
print(emu.ALU.vRAM)

# libs and statics
import copy
from time import sleep
DEBUG = True

# ALU
class ALU:
    # define memory and stuff
    eRAM = [0x0] * 0x80
    vRAM = [32] * 16
    eROM = []
    regA = 0
    regX = 0
    haltALU = False
    romName = ''

    
    # read system
    def Read(address):
        global eRAM
        global eROM

        if (address < 0x80):
            return ALU.eRAM[address]
        if (address >= 0x80) and (address < 0x80):
            return ALU.vRAM[address-0x80]
        if (address >= 0x90):
            return ALU.eROM[address-0x90]

    # write system
    def Write(address, value):
        global eRAM

        if (address < 0x80):
            ALU.eRAM[address] = value
        if (address >= 0x80):
            ALU.vRAM[address-0x80] = value
        
    def printScreen():
        global vRAM

        tmp = copy.deepcopy(ALU.vRAM)

        for i in range(len(tmp)):
            tmp[i] = chr(tmp[i])
        
        print(*tmp, sep='')
        
# Runner
class Ru:
    pc= 0

    # execute instruction
    def Execute():
        global pc

        # find instruction
        opcode = ALU.eROM[Ru.pc]
        Ru.pc+= 1

        match opcode:
            # region register A instructions
            case 0x80: # adda
                ALU.regA += 1
                ALU.regA %= 255

                # debug 
                if DEBUG:
                   print(f'adda, {ALU.regA}')

            case 0x81: # suba
                ALU.regA -= 1
                ALU.regA %= 255

                # debug 
                if DEBUG:
                    print('suba')
                
            case 0x82: # awta
                ALU.Write(ALU.Read(Ru.pc + 0x90), ALU.regA)
                Ru.pc+= 1

                # debug 
                if DEBUG:                
                    print(f'awta, {ALU.regA}')

            case 0x83: # rdaa
                ALU.regA = ALU.Read(Ru.pc + 0x90)
                Ru.pc+= 1

                # debug 
                if DEBUG:
                    print('rdaa')

            case 0x87: # seta
                ALU.regA = ALU.Read(Ru.pc + 0x90)
                Ru.pc+= 1 

                # debug 
                if DEBUG:                
                    print(f'seta, {ALU.regA}')

            case 0x8A: # bea
                val1 = ALU.Read(Ru.pc + 0x90)
                Ru.pc += 1
                val2 = ALU.Read(Ru.pc + 0x90)

                # debug
                if DEBUG:
                    print(f'bea, {val1}/{val2}')

                # do branch
                if (val1 == ALU.regA):
                    Ru.pc = val2
                else:
                    Ru.pc += 1

            # region register X instructions
            case 0xA0: # addx
                ALU.regX += 1
                ALU.regX %= 255

                # debug 
                if DEBUG:
                   print(f'addx, {ALU.regX}')

            case 0xA1: # subx
                ALU.regX -= 1
                ALU.regX %= 255

                # debug 
                if DEBUG:
                    print('subx')
                
            case 0xA2: # awtx
                ALU.Write(ALU.Read(Ru.pc + 0x90), ALU.regX)
                Ru.pc+= 1

                # debug 
                if DEBUG:                
                    print(f'awtx, {ALU.regX}')

            case 0xA3: # rdax
                ALU.regX = ALU.Read(Ru.pc + 0x90)
                Ru.pc+= 1

                # debug 
                if DEBUG:
                    print('rdax')

            case 0xA7: # setx
                ALU.regX = ALU.Read(Ru.pc + 0x90)
                Ru.pc+= 1 

                # debug 
                if DEBUG:                
                    print(f'setx, {ALU.regX}')

            case 0xAA:
                ALU.Write(ALU.regA, ALU.regX)

                # debug 
                if DEBUG:
                    print('awxx')

            # region misc
            case 0x84: # hlt
                ALU.haltALU = True

                # debug 
                if DEBUG:
                    print('hlt, end operation')

            case 0x85: # upd
                ALU.printScreen()

                # debug 
                if DEBUG:
                    print('upd')
                
            case 0x88: # jmp
                Ru.pc = ALU.Read(Ru.pc + 0x90)

                # debug 
                if DEBUG:                
                    print(f'jmp, {Ru.pc}')

            case _:
                print(f'unknown {Ru.pc}')
    

    # run program
    def run():
        while not(ALU.haltALU):
            Ru.Execute()
            sleep(0.00001)

        #region functions
    def importBytes(file):
        """
        Loads file into hexadecimal
        """
        with open(file, 'rb') as f:
            r = list(f.read())
            return r
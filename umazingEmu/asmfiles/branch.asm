; loop branch until register is at 128
adda
bea 128 5
jmp 0

; another loop branch but this time its at 97
suba 
bea 97 11
jmp 5

; dump character into vram and halt
awta 128
upd
hlt
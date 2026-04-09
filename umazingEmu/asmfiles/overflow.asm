; overflow
; keep increasing register until it reaches rom and then increase register X by 1
mark:
    adda
    addx
    awxx
    bea 140 cng
    jmp mark

cng:
    seta 0
    upd
    jmp mark
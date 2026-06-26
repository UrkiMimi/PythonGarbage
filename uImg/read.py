# libs
import pygame, sys, zlib

# open image 
with open('tachyon.uim', 'rb') as f:
    uim = list(f.read())

# get width and height
index = 5
width = ''
height = ''

# width loop
while (uim[index] != 44):
    width += chr(uim[index])
    index+=1

index += 1 

# height loop
while (uim[index] != 78):
    height += chr(uim[index])
    index+=1

# convert to int
width = int(width)
height = int(height)


# decompress data and read image
dat = uim[16:]
dat = bytes(dat)
dat = zlib.decompress(dat)
dat = list(dat)


# initalize pygame
pygame.init()
screen = pygame.display.set_mode((width, height))

def drawUIM():
    index = 0

    # image loop
    for y in range(height):
        for x in range(width):
            # determine color
            color = (dat[index], dat[index+1], dat[index+2])
            
            index+=3

            # render pixel
            pygame.draw.rect(screen, color, (x,y,1,1))

# draw image
drawUIM()
pygame.display.flip()

# persistence
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
import pygame, sys, math
import random as rand
from scipy import signal
import numpy as np

# init
pygame.init()
window = pygame.display.set_mode((480, 360), 0, 0)
pygame.display.set_caption("sorting algorithm but i spilled milk on it")
pygame.mixer.init(22050, size=-16, channels=1, buffer=512)


# timing init
clock = pygame.time.Clock()


# constants
RED = (255, 0, 0)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
SAMPLE_RATE = 22050
LINES = 100

# make array
array = []
for i in range(LINES):
    array.append((i/LINES)*100)


# region functions
# real
def draw_everything(pick = 0):
    # setup
    pSize = 480 / len(array)
    scale = 360 / 100
    color = WHITE

    # draw everything
    for x in range(len(array)):
        if pick == x:
            color = RED
        else:
            color = WHITE

        pygame.draw.rect(window, color, (x * pSize, 360 - (array[x] * scale), pSize, 360))


# FUCK
def generate_wave(freq, duration=0.1, vol=0.3):
    frames = int(duration * SAMPLE_RATE)
    t = np.linspace(0, duration, frames, endpoint=False)

    #this just generates a wave idk i want a square wave
    wave = (signal.square(2 * np.pi * freq * t) * vol * 32767).astype(np.int16)

    # i hate stereo audio
    channelAmount = pygame.mixer.get_init()[2]
    
    if channelAmount == 2:
        wave = np.column_stack((wave, wave))
 
    return pygame.sndarray.make_sound(wave)

def value_to_tone(value):
    return (array[value] * 4)  + 200



#screen refresh
def screenRefresh(pick = 0, playAudio = True):
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
    
    clock.tick(240)
    window.fill(BLACK)
    draw_everything(pick)

    # generate audio shit idk fhdsajkfhdsjklfdaskl
    if playAudio: 
        pygame.mixer.stop()
        generate_wave(value_to_tone(pick)).play()
    pygame.display.flip()


# shuffles list
def shuffle():
    for i in range(1024):
        one = rand.randint(0, len(array) - 1)
        two = rand.randint(0, len(array) - 1)

        # switch
        bkup = array[one]
        array[one] = array[two]
        array[two] = bkup
        
        # to make the shuffle pass not take as much time due to refresh concerns
        if ((i % 30) == 0):
            screenRefresh(one)

# region algorithms
# insertion sort
def insertionSort():
    rate = 0

    for i in range(1, len(array)):
        key = array[i]
        
        # move shit arround
        j = i - 1
        while j >= 0 and key < array[j]:
            array[j + 1] = array[j]
            j -= 1
            
            rate+=1

            if (rate % 20) == 0:
                screenRefresh(j)

        # replace
        array[j + 1] = key
            

# divison shit
def divisionSort():
    base = sorted(array)
    rate = 0

    # sort 
    while (array != base):
        for i in range(len(array)):
            one = i
            two = math.floor(one / rand.uniform(1, 1.2))

            # array
            if (array[one] < array[two]):
                bkup = array[one]
                array[one] = array[two]
                array[two] = bkup

                if (i % 5) == 0:
                    screenRefresh(one)


# cocktail sort
def cocktailSort():
    n = len(array)
    start = 0
    end = n-1
    swap = True

    while (swap == True):
        # swap
        swap = False

        # move to right

        for i in range(start, end):
            if (array[i] > array[i + 1]):
                array[i], array[i+1] = array[i+1], array[i]
                swap = True

                if (i % 20) == 0:
                    screenRefresh(i)

        # then to left
        for i in range(end-1, start-1, -1):
            if (array[i] > array[i + 1]):
                array[i], array[i+1] = array[i+1], array[i]
                swap = True

                if (i % 20) == 0:
                    screenRefresh(i)


# region program
shuffle()
pygame.time.wait(500)

insertionSort()
#divisionSort()
#cocktailSort()

while True: 
    screenRefresh(playAudio=False)
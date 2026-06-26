import math
from PIL import Image
import zlib

# file format
def uImg(width, height, data):
    ### header and metadata
    tmp = [0] * 16

    # add header to first four bytes
    headerTex = 'uImg'
    for i in range(len(headerTex)):
        tmp[i] = ord(headerTex[i])

    
    ### add width and height
    # width
    index = 5
    for i in range(len(str(width))):
        tmp[index] = ord(str(width)[i])
        index+=1

    # seperator then height
    tmp[index] = ord(',')
    index+=1
    
    for i in range(len(str(height))):
        tmp[index] = ord(str(height)[i])
        index+=1

    # end byte
    tmp[index] = ord('N')
    
    # image data
    tmp += zlib.compress(bytes(data), level=9)

    return bytes(tmp)

#returns 8bit array of each channel
def imageToArray(imagePath):
    # Import and scale image
    image = Image.open(imagePath).convert('RGB')
    width, height = [round(image.size[0]), round(image.size[1])]
    image = image.resize((width, height))

    # Seperate image by channel
    pixelR = image.getchannel('R').getdata()
    pixelG = image.getchannel('G').getdata()
    pixelB = image.getchannel('B').getdata()

    tmp = []

    # add to array
    for r in range(width*height):
        tmp.append(pixelR[r])
        tmp.append(pixelG[r])
        tmp.append(pixelB[r])

    return tmp


with open('smoker.uim' , 'wb') as f:
   imgArray = imageToArray('image copy.png')
   f.write(uImg(1546,1252,imgArray))
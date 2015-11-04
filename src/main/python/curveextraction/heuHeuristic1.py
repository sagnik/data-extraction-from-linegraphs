import sys
from PIL import Image
import numpy as np
import colorsys
from operator import itemgetter


def returnClosestrange(val):
    coloranges = range(0, 360, 10)
    mindif = 10000
    minindex = 0
    for index, item in enumerate(coloranges):
        dif = abs(item - val)
        if dif < mindif:
            mindif = dif
            minindex = index
    return coloranges[minindex]


imagefile = sys.argv[1]
print imagefile
imagetobesaved = imagefile[:-4] + "-hued.png"
im = Image.open(imagefile).convert('RGB')
imagedata = np.asarray(im)

huedict = {}
for i in range(0, imagedata.shape[0]):
    for j in range(0, imagedata.shape[1]):
        rgbcolor = imagedata[i][j]
        r = rgbcolor[0]
        g = rgbcolor[1]
        b = rgbcolor[2]
        h, s, v = colorsys.rgb_to_hsv(rgbcolor[0] / 255., rgbcolor[1] / 255., rgbcolor[2] / 255.)
        h = int(360 * h)
        s = int(100 * s)
        v = int(100 * v)
        if v > 5 and s > 10:
            if h in huedict:
                huedict[h].append(((i, j), (h, s, v), (r, g, b)))
            else:
                huedict[h] = [((i, j), (h, s, v), (r, g, b))]

modhuedict = {}
for item in huedict.keys():
    if returnClosestrange(item) in modhuedict:
        for var in huedict[item]:
            modhuedict[returnClosestrange(item)].append(var)
    else:
        modhuedict[returnClosestrange(item)] = []
        for var in huedict[item]:
            modhuedict[returnClosestrange(item)].append(var)

modhuedictlen = {}
for index, item in enumerate(modhuedict.keys()):
    modhuedictlen[item] = len(modhuedict[item])

modhuesorted = sorted(modhuedictlen.items(), key=itemgetter(1), reverse=True)
nocolor = 1
colorfreq = [x[1] for x in modhuesorted]
for i in range(1, len(colorfreq)):
    if colorfreq[i - 1] - colorfreq[i] > 0.5 * colorfreq[i - 1]:
        break
    else:
        nocolor += 1

finalcolors = modhuesorted[0:nocolor]
print "no of base colors", nocolor
imagedatacopy = np.zeros(imagedata.shape)
imagedatacopy[:, :] = [255, 255, 255]
with open("predictedbasecolors-h1", "a") as f:
    f.write(imagefile + "," + str(nocolor) + "\n")
for item in finalcolors:
    # print item,item[0]
    pixelist = modhuedict[item[0]]
    for item2 in pixelist:
        pixel = item2[0]
        pixelcolor = np.asarray(list(item2[-1]))
        # print pixel,pixelcolor
        pixelx = pixel[0]
        pixely = pixel[1]
        imagedatacopy[pixelx][pixely] = pixelcolor

imPIL = Image.fromarray(np.uint8(imagedatacopy))
imPIL.save(imagetobesaved)
# im.show()

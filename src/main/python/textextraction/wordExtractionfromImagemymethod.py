# input: one png image
# output: word locations from the png image

from __future__ import division
from skimage import io, color
from skimage.feature import canny
# from skimage.filters import canny
import sys
from scipy.ndimage.measurements import label
import os
from PIL import Image, ImageDraw
import numpy as np
import scipy as sp
import colorsys

HORIZONTALTHRESHOLD = 1000
VERTICALTHRESHOLD = 1000


def getBoundingBoxfromPixels(indices):
    b = [min(indices[0][0]), min(indices[0][1]), max(indices[0][0]), max(indices[0][1])]  # x1,y1,x2,y2
    return b


def getBoundingBoxfromPixelsLarge(indices):
    b = [min(indices[0][0]), min(indices[0][1]), max(indices[0][0]), max(indices[0][1])]  # x1,y1,x2,y2
    return b


def boundingBoxiConsumedbyj(b1, b2):
    if b1[0] >= b2[0] and b1[2] <= b2[2] and b1[1] >= b2[1] and b1[3] <= b2[3]:
        return True
    else:
        return False


def iswithintenpercent(box, imgwidth):
    if box[1] < 0.05 * imgwidth:
        return True
    else:
        return False


def rectmanDist(Q, R):
    box1 = Q
    box2 = R
    xOverlap = max(0, min(box1[2], box2[2]) - max(box1[0], box2[0]))
    yOverlap = max(0, min(box1[3], box2[3]) - max(box1[1], box2[1]))
    if (xOverlap * yOverlap) > 0:
        return 0
    dY1 = 0
    dY2 = 0
    dX1 = 0
    dX2 = 0
    if (Q[3] < R[1]):
        dY1 = R[1] - Q[3]
    if (Q[1] > R[3]):
        dY2 = Q[1] - R[3]
    if (Q[2] < R[0]):
        dX1 = R[0] - Q[2]
    if (Q[0] > R[2]):
        dX2 = Q[0] - R[2]
    return (dX1 + dX2 + dY1 + dY2)


def rectmanDistVertical(Q, R):
    box1 = Q
    box2 = R
    xOverlap = max(0, min(box1[2], box2[2]) - max(box1[0], box2[0]))
    yOverlap = max(0, min(box1[3], box2[3]) - max(box1[1], box2[1]))
    if (xOverlap * yOverlap) > 0:
        return True
    dY1 = 0
    dY2 = 0
    dX1 = 0
    dX2 = 0
    if (Q[3] < R[1]):
        dY1 = R[1] - Q[3]
    if (Q[1] > R[3]):
        dY2 = Q[1] - R[3]
    if (Q[2] < R[0]):
        dX1 = R[0] - Q[2]
    if (Q[0] > R[2]):
        dX2 = Q[0] - R[2]
    if (dY1 + dY2) < 2:  # horizontal distance is very short between the rectangles
        if (dX1 + dX2) < VERTICALTHRESHOLD:
            return True
    else:
        return False


def rectmanDistHorizontal(Q, R, imgwidth):
    box1 = Q
    box2 = R
    # if one of the boxes are within 10% from the left, use vertical merging
    # else use horizontal merging.
    if iswithintenpercent(Q, imgwidth) or iswithintenpercent(R, imgwidth):
        return rectmanDistVertical(Q, R)
    xOverlap = max(0, min(box1[2], box2[2]) - max(box1[0], box2[0]))
    yOverlap = max(0, min(box1[3], box2[3]) - max(box1[1], box2[1]))
    if (xOverlap * yOverlap) > 0:
        return True
    dY1 = 0
    dY2 = 0
    dX1 = 0
    dX2 = 0
    if (Q[3] < R[1]):
        dY1 = R[1] - Q[3]
    if (Q[1] > R[3]):
        dY2 = Q[1] - R[3]
    if (Q[2] < R[0]):
        dX1 = R[0] - Q[2]
    if (Q[0] > R[2]):
        dX2 = Q[0] - R[2]
    if (dX1 + dX2) < 2:  # vertical distance is very short between the rectangles
        if (dY1 + dY2) < HORIZONTALTHRESHOLD:
            return True
    else:
        return False


def getDistHorizontal(Q, R):
    box1 = Q
    box2 = R
    xOverlap = max(0, min(box1[2], box2[2]) - max(box1[0], box2[0]))
    yOverlap = max(0, min(box1[3], box2[3]) - max(box1[1], box2[1]))
    if yOverlap > 0:
        return 0
    dY1 = 0
    dY2 = 0
    dX1 = 0
    dX2 = 0
    if (Q[3] < R[1]):
        dY1 = R[1] - Q[3]
    if (Q[1] > R[3]):
        dY2 = Q[1] - R[3]
    if (Q[2] < R[0]):
        dX1 = R[0] - Q[2]
    if (Q[0] > R[2]):
        dX2 = Q[0] - R[2]
    if (dX1 + dX2) < 2:  # vertical distance is very short between the rectangles
        return (dY1 + dY2)
    else:
        return 0


def getDistVertical(Q, R):
    box1 = Q
    box2 = R
    xOverlap = max(0, min(box1[2], box2[2]) - max(box1[0], box2[0]))
    yOverlap = max(0, min(box1[3], box2[3]) - max(box1[1], box2[1]))
    if xOverlap > 0:
        return 0
    dY1 = 0
    dY2 = 0
    dX1 = 0
    dX2 = 0
    if (Q[3] < R[1]):
        dY1 = R[1] - Q[3]
    if (Q[1] > R[3]):
        dY2 = Q[1] - R[3]
    if (Q[2] < R[0]):
        dX1 = R[0] - Q[2]
    if (Q[0] > R[2]):
        dX2 = Q[0] - R[2]
    if (dY1 + dY2) < 2:  # vertical distance is very short between the rectangles
        return (dX1 + dX2)
    else:
        return 0


def getcolorpercentage(imgsec):
    totalarea = imgsec.shape[0] * imgsec.shape[1]
    colorpixels = 0
    for i in range(0, imgsec.shape[0]):
        for j in range(0, imgsec.shape[1]):
            h, s, v = imgsec[i][j]
            if (v > 5 and s > 10):  # not white, black,grey
                colorpixels += 1
    try:
        return (colorpixels / totalarea) * 100
    except ZeroDivisionError:
        return 100


def rectmanDist(Q, R):
    box1 = Q
    box2 = R
    xOverlap = max(0, min(box1[2], box2[2]) - max(box1[0], box2[0]))
    yOverlap = max(0, min(box1[3], box2[3]) - max(box1[1], box2[1]))
    if (xOverlap * yOverlap) > 0:
        return 0
    dY1 = 0
    dY2 = 0
    dX1 = 0
    dX2 = 0
    if (Q[3] < R[1]):
        dY1 = R[1] - Q[3]
    if (Q[1] > R[3]):
        dY2 = Q[1] - R[3]
    if (Q[2] < R[0]):
        dX1 = R[0] - Q[2]
    if (Q[0] > R[2]):
        dX2 = Q[0] - R[2]
    return (dX1 + dX2 + dY1 + dY2)


def mergeOnce(imgray, finalBoundingboxesFiltered, imgwidth):
    edges = sp.zeros(imgray.shape)
    labeldict = {}
    colornumber = [0]
    nomerges = 0
    for i in range(0, len(finalBoundingboxesFiltered)):
        item1 = finalBoundingboxesFiltered[i]
        stritem1 = ','.join([str(x) for x in item1])
        currentcolors = [labeldict[item] for item in labeldict.keys()]
        if currentcolors:
            for color1 in currentcolors:
                colornumber.append(color1)
        currentcolornumber = max(colornumber) + 1
        if not stritem1 in labeldict:
            labeldict[stritem1] = currentcolornumber
        else:
            currentcolornumber = labeldict[stritem1]
        edges[item1[0]:item1[2], item1[1]:item1[3]] = currentcolornumber
        for j in range(i + 1, len(finalBoundingboxesFiltered)):
            item2 = finalBoundingboxesFiltered[j]
            stritem2 = ','.join([str(x) for x in item2])
            # if rectmanDist(item1,item2)<max(HORIZONTALTHRESHOLD,VERTICALTHRESHOLD):
            if rectmanDistHorizontal(item1, item2, imgwidth):
                nomerges += 1
                if stritem2 in labeldict:
                    currentcolornumber = labeldict[stritem2]
                    edges[item1[0]:item1[2], item1[1]:item1[3]] = currentcolornumber
                    labeldict[stritem1] = currentcolornumber
                else:
                    labeldict[stritem2] = currentcolornumber
                edges[item2[0]:item2[2], item2[1]:item2[3]] = currentcolornumber

    labeled_array = edges.copy()
    num_features = max(colornumber) + 1

    temp = []
    for i in range(1, num_features + 1):
        label_i_indices = [(labeled_array == i).nonzero()]
        if len(label_i_indices[0][0]) > 0:
            temp.append(getBoundingBoxfromPixelsLarge(label_i_indices))

    print "after merging boundingboxes", len(temp)
    interimBoundingboxes = list(temp)
    interimBoundingboxesDict = {}
    for item in interimBoundingboxes:
        interimBoundingboxesDict[','.join([str(i) for i in item])] = True

    for item1 in temp:
        toberemoved = []
        for item2 in temp:
            if (item1 != item2):
                result = boundingBoxiConsumedbyj(item1, item2)
                if result:
                    toberemoved.append(item1)
        for item in toberemoved:
            interimBoundingboxesDict[','.join([str(i) for i in item])] = False

    finalBoundingboxes = []
    for key in interimBoundingboxesDict.keys():
        if interimBoundingboxesDict[key]:
            item = [int(x) for x in key.split(',')]
            finalBoundingboxes.append(item)

    print "number of merges", nomerges
    return (finalBoundingboxes, nomerges)


def getcandidateCCs(imgLoc):
    img = io.imread(imgLoc)
    imgray = color.rgb2gray(img)
    edge = canny(imgray)
    print "edge found"
    s = [[1, 1, 1], [1, 1, 1], [1, 1, 1]]
    labeled_array, num_features = label(edge, structure=s)
    print "labeling done"
    temp = []
    print "started with", num_features, "connected components"
    for i in range(1, num_features + 1):
        label_i_indices = [(labeled_array == i).nonzero()]
        if getBoundingBoxfromPixels(label_i_indices):
            temp.append(getBoundingBoxfromPixels(label_i_indices))

    print "started with", len(temp), "bounding boxes"
    imgarea = (img.shape[0] * img.shape[1])
    print imgarea
    interimBoundingboxes = []
    for item in temp:
        if not (item[2] - item[0]) * (item[3] - item[1]) > 0.01 * imgarea:
            if (item[2] - item[0]) > 5 or (item[3] - item[1]) > 5:
                interimBoundingboxes.append(item)

    interimBoundingboxesDict = {}
    for item in interimBoundingboxes:
        interimBoundingboxesDict[','.join([str(i) for i in item])] = True

    for item1 in interimBoundingboxes:
        toberemoved = []
        for item2 in interimBoundingboxes:
            if (item1 != item2):
                result = boundingBoxiConsumedbyj(item1, item2)
                if result:
                    toberemoved.append(item1)
        for item in toberemoved:
            interimBoundingboxesDict[','.join([str(i) for i in item])] = False

    finalBoundingboxes = []
    for key in interimBoundingboxesDict.keys():
        if interimBoundingboxesDict[key]:
            item = [int(x) for x in key.split(',')]
            finalBoundingboxes.append(item)

    # starting to merge: only merging overlapping boxes here
    finalBoundingboxesFiltered = finalBoundingboxes
    print "starting to merge"
    edges = sp.zeros(edge.shape)
    labeldict = {}
    colornumber = [0]
    for i in range(0, len(finalBoundingboxesFiltered)):
        item1 = finalBoundingboxesFiltered[i]
        stritem1 = ','.join([str(x) for x in item1])
        currentcolors = [labeldict[item] for item in labeldict.keys()]

        if currentcolors:
            for color1 in currentcolors:
                colornumber.append(color1)

        currentcolornumber = max(colornumber) + 1
        if not stritem1 in labeldict:
            labeldict[stritem1] = currentcolornumber
        else:
            currentcolornumber = labeldict[stritem1]
        edges[item1[0]:item1[2], item1[1]:item1[3]] = currentcolornumber
        for j in range(i + 1, len(finalBoundingboxesFiltered)):
            item2 = finalBoundingboxesFiltered[j]
            stritem2 = ','.join([str(x) for x in item2])
            if rectmanDist(item1, item2) < 1:
                if stritem2 in labeldict:
                    currentcolornumber = labeldict[stritem2]
                    edges[item1[0]:item1[2], item1[1]:item1[3]] = currentcolornumber
                    labeldict[stritem1] = currentcolornumber
                else:
                    labeldict[stritem2] = currentcolornumber
                edges[item2[0]:item2[2], item2[1]:item2[3]] = currentcolornumber

    labeled_array = edges.copy()
    num_features = max(colornumber) + 1

    temp = []
    for i in range(1, num_features + 1):
        label_i_indices = [(labeled_array == i).nonzero()]
        if len(label_i_indices[0][0]) > 0:
            temp.append(getBoundingBoxfromPixelsLarge(label_i_indices))

    print "after merging boundingboxes", len(temp)

    interimBoundingboxes = list(temp)
    interimBoundingboxesDict = {}
    for item in interimBoundingboxes:
        interimBoundingboxesDict[','.join([str(i) for i in item])] = True

    for item1 in temp:
        toberemoved = []
        for item2 in temp:
            if (item1 != item2):
                result = boundingBoxiConsumedbyj(item1, item2)
                if result:
                    toberemoved.append(item1)
        for item in toberemoved:
            interimBoundingboxesDict[','.join([str(i) for i in item])] = False

    finalBoundingboxes = []
    for key in interimBoundingboxesDict.keys():
        if interimBoundingboxesDict[key]:
            item = [int(x) for x in key.split(',')]
            finalBoundingboxes.append(item)

    return finalBoundingboxes


def filterCCs(imgLoc, candidateCCs):
    im = Image.open(imgLoc).convert('RGB')
    imgheight = im.size[0]
    imgwidth = im.size[0]
    imagedata = np.asarray(im)
    print "calculating HSV", imagedata.shape
    huecolor = np.zeros(imagedata.shape)
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
            huecolor[i][j] = [h, s, v]
    print "HSV calulation done", imagedata.shape
    filteredCCs = []
    for box in candidateCCs:
        if getcolorpercentage(huecolor[box[0]:box[2], box[1]:box[3]]) < 6:
            filteredCCs.append(box)
    return filteredCCs


def getWords(imageloc, finalBoundingboxesFiltered):
    img = io.imread(imageloc)
    imgray = color.rgb2gray(img)
    horizontaldistances = []
    verticaldistances = []
    imgwidth = Image.open(imageloc).size[0]

    for i in range(0, len(finalBoundingboxesFiltered)):
        for j in range(i + 1, len(finalBoundingboxesFiltered)):
            item1 = finalBoundingboxesFiltered[i]
            item2 = finalBoundingboxesFiltered[j]
            h = getDistHorizontal(item1, item2)
            v = getDistVertical(item1, item2)
            if h != 0:
                horizontaldistances.append(h)
            if v != 0:
                verticaldistances.append(v)
    global HORIZONTALTHRESHOLD
    global VERTICALTHRESHOLD

    # print horizontaldistances,verticaldistances
    HORIZONTALTHRESHOLD = sorted(np.unique(horizontaldistances))[2] + 1
    VERTICALTHRESHOLD = sorted(np.unique(verticaldistances))[1] + 1
    print "using horizontal and vertical thresholds", HORIZONTALTHRESHOLD, VERTICALTHRESHOLD
    nomerges = 1
    while (nomerges):
        (finalBoundingboxesFiltered, nomerges) = mergeOnce(imgray, finalBoundingboxesFiltered, imgwidth)

    finalBoundingboxes = finalBoundingboxesFiltered
    return finalBoundingboxes


def main():
    imgLoc = sys.argv[1]
    imgDir, exactImageLoc = os.path.split(imgLoc)
    basedir = "/home/sagnik/data/linegraph-data/pngs/colorfigures/evaluation/textextraction/finalpredictedwords-doceng/sagnik/"
    imagetobesaved = basedir + "image/" + exactImageLoc[:-4] + "-wordpredicted.png"
    boxtobesaved = basedir + "boxloc/" + exactImageLoc[:-4] + "-wordpredicted.box"

    print "started getting candidate CCs"
    candidateCCs = getcandidateCCs(imgLoc)
    if candidateCCs:
        print "found candidate CCs, starting filtering...."
        filteredCCs = filterCCs(imgLoc, candidateCCs)
    else:
        print "found no candidate CC, returning empty"
        return
    if filteredCCs:
        print "found filtered CCs, combining them into words...."
        words = getWords(imgLoc, filteredCCs)
    else:
        print "found no filtered CC, returning empty"
        return
    if words:
        print "words formed"
        f = open(boxtobesaved, "w")
        pilImg = Image.open(imgLoc)
        draw = ImageDraw.Draw(pilImg)
        for item in words:
            box = [item[0] - 3, item[1] - 3, item[2] + 3, item[3] + 3]
            # draw.rectangle(box,outline="red")
            # f.write(",".join([str(x) for x in box])+"\n")
            draw.rectangle([box[1], box[0], box[3], box[2]], outline="green")

        pilImg.show(imagetobesaved)
        # pilImg.save(imagetobesaved)
        f.close()
    else:
        print "found no word, returning empty"
        return


if __name__ == "__main__":
    main()

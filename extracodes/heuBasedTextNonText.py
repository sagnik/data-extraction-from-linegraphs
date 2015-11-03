from __future__ import division
import sys
from PIL import Image,ImageDraw
import numpy as np
import colorsys
from operator import itemgetter
import os

def getcolorpercentage(imgsec):
	#print imgsec,imgsec.shape
	totalarea=imgsec.shape[0]*imgsec.shape[1]
	colorpixels=0
	for i in range(0,imgsec.shape[0]):
		for j in range(0,imgsec.shape[1]):
			h,s,v=imgsec[i][j]
			if (v > 5 and s>10): #not white, black,grey
				 colorpixels+=1
	try:
		return (colorpixels/totalarea)*100
	except ZeroDivisionError:
		return 100
	#return (colorpixels/totalarea)*100		
		
imagefile=sys.argv[1]
dir,actualimage=os.path.split(imagefile)
boxfile="/home/sagnik/linegraph-experiment-1/pngs/colorfigures/training/textextraction/goldstandardfortext/boxlocsgold/"\
	+actualimage[:-4]+"-textgold.box"
boxpredictedfile="/home/sagnik/linegraph-experiment-1/pngs/colorfigures/training/textextraction/goldstandardfortext/textpredictedhueboxlocs/"\
	+actualimage[:-4]+"-textpredictedhue.box"
imagepredictedfile="/home/sagnik/linegraph-experiment-1/pngs/colorfigures/training/textextraction/goldstandardfortext/textpredictedhueimage/"\
	+actualimage[:-4]+"-textpredictedhue.png"
print imagefile,boxfile
im=Image.open(imagefile).convert('RGB')
imgheight=im.size[0]
imgwidth=im.size[0]
	
print im.size
imagedata=np.asarray(im)
print imagedata.shape
#mid70percent=
huecolor=np.zeros(imagedata.shape)
for i in range(0,imagedata.shape[0]):
	for j in range(0,imagedata.shape[1]):
		rgbcolor=imagedata[i][j]
		r=rgbcolor[0]
		g=rgbcolor[1]
		b=rgbcolor[2]
		h,s,v=colorsys.rgb_to_hsv(rgbcolor[0]/255.,rgbcolor[1]/255.,rgbcolor[2]/255.)
		h=int(360*h)
		s=int(100*s)
		v=int(100*v)
		huecolor[i][j]=[h,s,v]

con=open(boxfile).read().split("\n")[:-1]
draw = ImageDraw.Draw(im)

f=open(boxpredictedfile,"w")
for line in con:
	box=[int(x) for x in line.split(";")[0].split(",")]
	#box=[box[1],box[0],box[3],box[2]]
	if getcolorpercentage(huecolor[box[0]:box[2],box[1]:box[3]])>5:
		draw.rectangle([box[1],box[0],box[3],box[2]],outline="red")
		f.write(line+";predicted:0\n")
	#elif (box[2]-box[0]<5) or (box[3]-box[1]<5): #heuristic 1: remove very small boxes 
	#	draw.rectangle([box[1],box[0],box[3],box[2]],outline="red")
	#	f.write(line+";predicted:0\n")
	#elif (box[3]-box[1])/(box[2]-box[0]) > 3: #heuristic 2: remove on aspect ratio, bad idea?
	#need to develop a heuristic based on distribution of predicted text/non text
	#elif box[2]>0.3*) or (box[3]-box[1]<5):
	else:	 
		draw.rectangle([box[1],box[0],box[3],box[2]],outline="green")				
		f.write(line+";predicted:1\n")

im.save(imagepredictedfile)	


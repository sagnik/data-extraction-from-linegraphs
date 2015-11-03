from __future__ import division
from skimage import io,color
from skimage.feature import canny
#from skimage.filters import canny
import sys
from scipy.ndimage.measurements import label
import os
from PIL import Image,ImageDraw
import numpy as np
from matplotlib import pyplot as plt
from skimage.transform import rescale
import scipy as sp
import simplejson as json
from rtree import index
from scipy.ndimage.morphology import binary_closing

def show_img(img):
	width = img.shape[1]/75.0
	height = img.shape[0]*width/img.shape[1]
	f = plt.figure(figsize=(width, height))
	plt.imshow(img)
	plt.show()

def getBoundingBoxfromPixels(indices,(w,h)):
        b=[min(indices[0][0]),min(indices[0][1]),max(indices[0][0]),max(indices[0][1])] #x1,y1,x2,y2
	a=(b[2]-b[0])*(b[3]-b[1])
	return b

def getBoundingBoxfromPixelsLarge(indices,(w,h)):
        b=[min(indices[0][0]),min(indices[0][1]),max(indices[0][0]),max(indices[0][1])] #x1,y1,x2,y2
	return b
	
def boundingBoxiConsumedbyj(b1,b2):
	if b1[0]>=b2[0] and b1[2]<=b2[2] and b1[1]>=b2[1] and b1[3]<=b2[3]:
		#print "true"
		return True
	else:
		return False


def rectmanDist(Q,R):
	box1=Q
	box2=R
	xOverlap=max(0,min(box1[2],box2[2])-max(box1[0],box2[0])) 
	yOverlap=max(0,min(box1[3],box2[3])-max(box1[1],box2[1]))
	if (xOverlap*yOverlap)>0:
		#print "overlap found"
		return 0
	dY1=0 
	dY2=0 
	dX1=0 
	dX2=0
 
	if (Q[3]<R[1]):
		dY1=R[1]-Q[3]
 
	if (Q[1]>R[3]):
		dY2=Q[1]-R[3]
 
	if (Q[2]<R[0]):
		dX1=R[0]-Q[2]
 
	if (Q[0]>R[2]):
		dX2=Q[0]-R[2]
	#print Q," ",R," ",(dX1+dX2+dY1+dY2)
	return (dX1+dX2+dY1+dY2)

def main():
	imgLoc=sys.argv[1]
	imgDir,exactImageLoc=os.path.split(imgLoc)
	jsonloc="modjsons/"+exactImageLoc[:-4]+".json"
	imagetexts=json.load(open(jsonloc))['ImageText']
	#print imagetexts
	
	rtreeidx=index.Index()
	for ind,imagetext in enumerate(imagetexts):
		rtreeidx.insert(ind,tuple(imagetext['TextBB']))

	
	img=io.imread(imgLoc)
	imgray=color.rgb2gray(img)
	edge=canny(imgray)
	print edge.shape
	print "edge found"
	show_img(edge)
	s = [[1,1,],[1,1]]
	edge = binary_closing(edge,s) 
	s = [[1,1,1],[1,1,1],[1,1,1]]
	labeled_array,num_features=label(edge,structure=s)
	show_img(edge)
	print "labeling done"
	temp=[]
	print "started with",num_features,"connected components"
	
	for i in range(1,num_features+1):
		label_i_indices = [(labeled_array == i).nonzero()]
		if getBoundingBoxfromPixels(label_i_indices,(img.shape[1],img.shape[0])):
			temp.append(getBoundingBoxfromPixels(label_i_indices,(img.shape[1],img.shape[0])))
			
	print "started with",len(temp),"bounding boxes"
	imgarea=(img.shape[0]*img.shape[1])
	print imgarea
	interimBoundingboxes=[]
	for item in temp:
		if not (item[2]-item[0])*(item[3]-item[1]) > 0.3*imgarea:
			#if (item[2]-item[0])>5 or (item[3]-item[1])>5:
			interimBoundingboxes.append(item)
	
	interimBoundingboxesDict={}
	for item in interimBoundingboxes:
		interimBoundingboxesDict[','.join([str(i) for i in item])]=True
	
	for item1 in interimBoundingboxes:
		toberemoved=[]
		for item2 in interimBoundingboxes:
			if (item1!=item2):
				result=boundingBoxiConsumedbyj(item1,item2)
				if result:
					toberemoved.append(item1)
		for item in toberemoved:
			interimBoundingboxesDict[','.join([str(i) for i in item])]=False
			
	finalBoundingboxes=[]
	for key in interimBoundingboxesDict.keys():
		if interimBoundingboxesDict[key]:
			item=[int(x) for x in key.split(',')]
			finalBoundingboxes.append(item)
		
	finalBoundingboxesFiltered=finalBoundingboxes
	print "starting to merge" 
	edges=sp.zeros(edge.shape)	
	labeldict={}
	colornumber=[0]
	for i in range(0,len(finalBoundingboxesFiltered)):
		item1=finalBoundingboxesFiltered[i]
		stritem1=','.join([str(x) for x in item1])
		currentcolors=[labeldict[item] for item in labeldict.keys()]

		if currentcolors:
			for color1 in currentcolors:
				colornumber.append(color1)
	
		currentcolornumber=max(colornumber)+1
		if not stritem1 in labeldict:
			labeldict[stritem1]=currentcolornumber
		else:
			currentcolornumber=labeldict[stritem1]
		edges[item1[0]:item1[2],item1[1]:item1[3]]=currentcolornumber
		for j in range(i+1,len(finalBoundingboxesFiltered)):
			item2=finalBoundingboxesFiltered[j]
			stritem2=','.join([str(x) for x in item2])
			if rectmanDist(item1,item2)<1:
			#if rectmanDistHorizontal(item1,item2)<10:
				#print item1,"merged with",item2,"with",currentcolornumber
				if stritem2 in labeldict:
					currentcolornumber=labeldict[stritem2]
					edges[item1[0]:item1[2],item1[1]:item1[3]]=currentcolornumber
					labeldict[stritem1]=currentcolornumber
				else:
					labeldict[stritem2]=currentcolornumber
				edges[item2[0]:item2[2],item2[1]:item2[3]]=currentcolornumber
					

	
	labeled_array=edges.copy()
	num_features=max(colornumber)+1
	
	temp=[]
	for i in range(1,num_features+1):
		label_i_indices = [(labeled_array == i).nonzero()]
		#print i,len(label_i_indices[0][0])
		if len(label_i_indices[0][0])>0:
			temp.append(getBoundingBoxfromPixelsLarge(label_i_indices,(img.shape[1],img.shape[0])))
			

	print "after merging boundingboxes",len(temp)

	interimBoundingboxes=list(temp)
	interimBoundingboxesDict={}
	for item in interimBoundingboxes:
		interimBoundingboxesDict[','.join([str(i) for i in item])]=True
	
	for item1 in temp:
		toberemoved=[]
		for item2 in temp:
			if (item1!=item2):
				result=boundingBoxiConsumedbyj(item1,item2)
				if result:
					toberemoved.append(item1)
		for item in toberemoved:
			interimBoundingboxesDict[','.join([str(i) for i in item])]=False
			
	finalBoundingboxes=[]
	for key in interimBoundingboxesDict.keys():
		if interimBoundingboxesDict[key]:
			item=[int(x) for x in key.split(',')]
			finalBoundingboxes.append(item)

	pilImg=Image.fromarray(img)
	draw = ImageDraw.Draw(pilImg)
	#boxLoc=os.path.join(imgDir,"textextraction/goldstandardfortext/boxlocsgold/"+exactImageLoc[:-4]+"-textgold.box")
	#boxLoc="textextraction/goldstandardfortext/boxlocsgold/"+exactImageLoc[:-4]+"-textgold.box"
	#f=open(boxLoc,"w")
	for item in finalBoundingboxes:
		#currentboxintersects=list(rtreeidx.intersection((item[1],item[0],item[3],item[2])))
		#if len(currentboxintersects)>0:
			#print [imagetexts[x]['Text'] for x in currentboxintersects]
		draw.rectangle([item[1],item[0],item[3],item[2]],outline="blue")
		#f.write(','.join([str(x) for x in item])+";1\n")
		#print "yes"
		#	istext=True
		#if not istext:
		#else:
			#draw.rectangle([item[1],item[0],item[3],item[2]],outline="red")
			#f.write(','.join([str(x) for x in item])+";0\n")
		#print item,((item[2]-item[0])*(item[3]-item[1]))/imgarea
	pilImg.show()
	
	#pilImg.save(os.path.join(imgDir,"textextraction/goldstandardfortext/images",exactImageLoc[:-4]+"-textgold.png"))
	#f.close()

	

if __name__ == "__main__":
	main()


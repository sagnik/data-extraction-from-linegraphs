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

OVERLAPRATIOTHRESHOLD=0.75

def show_img(img):
	width = img.shape[1]/75.0
	height = img.shape[0]*width/img.shape[1]
	f = plt.figure(figsize=(width, height))
	plt.imshow(img)
	plt.show()

def mergeBoxes(b1,b2):
	return[min(b1[0],b2[0]),min(b1[1],b2[1]),max(b1[2],b2[2]),max(b1[3],b2[3])]

def significantOverlap(box1,box2): #if the overlap between our rectangle and text area in gt is greater than 
#50% of our rectangle. Assuming our rectangle is way smaller than the text area. Otherwise use intersection/
#union formula, see http://pascallin.ecs.soton.ac.uk/challenges/VOC/voc2012/htmldoc/devkit_doc.html#SECTION00054000000000000000
	#print box1,box2
	xOverlap=max(0,min(box1[2],box2[2])-max(box1[0],box2[0])) 
	yOverlap=max(0,min(box1[3],box2[3])-max(box1[1],box2[1]))
	overLap=xOverlap*yOverlap
	#union=mergeBoxes(box1,box2)
	b1=box1
	b2=box2
	b1area=(b1[2]-b1[0])*(b1[3]-b1[1])
	b2area=(b2[2]-b2[0])*(b2[3]-b2[1])
	#if overLap>0:
	#	print box1,box2,overLap,(b1area+b2area),overLap/(b1area+b2area)
	if overLap/min(b1area,b2area) > OVERLAPRATIOTHRESHOLD:
		#print "overlap found"
		return True
	else:
		return False

def getBoundingBoxfromPixels(indices,(w,h)):
        b=[min(indices[0][0]),min(indices[0][1]),max(indices[0][0]),max(indices[0][1])] #x1,y1,x2,y2
	'''
	if (b[2]-b[0])<0.01*w:
		return None
	elif (b[3]-b[1])<0.01*h:
		return None
	else:
		return b
	'''	
	a=(b[2]-b[0])*(b[3]-b[1])
	if a>100:
		return b
	else:
		return None

def getBoundingBoxfromPixelsLarge(indices,(w,h)):
        b=[min(indices[0][0]),min(indices[0][1]),max(indices[0][0]),max(indices[0][1])] #x1,y1,x2,y2
	return b
	
def boundingBoxiConsumesjSpecial(b1,b2,(w,h)):
	#we will output True if b1 consumes b2 and b1 is significantly large
	#this means we are looking for smaller bounding boxes. If this returns True, b1
	#gets deleted. 
	if b1[0]<=b2[0] and b1[2]>=b2[2] and b1[1]<=b2[1] and b1[3]>=b2[3]:
		if (b1[2]-b1[0])>0.01*w or (b1[3]-b1[1])>0.01*h:
			return True
		else:
			return False 
	else:
		return False

def boundingBoxiConsumedbyj(b1,b2):
	if b1[0]>=b2[0] and b1[2]<=b2[2] and b1[1]>=b2[1] and b1[3]<=b2[3]:
		#print "true"
		return True
	else:
		return False

def boundingBoxiConsumedbyjorMerge(b1,b2):
	b1area=(b1[2]-b1[0])*(b1[3]-b1[1])
	b2area=(b2[2]-b2[0])*(b2[3]-b2[1])
			
	if b1[0]>=b2[0] and b1[2]<=b2[2] and b1[1]>=b2[1] and b1[3]<=b2[3]:
		return True
		#we can discard the smaller box if two bounding boxes overlap significantly
	elif significantOverlap(b1,b2) and b1area<b2area:
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
	img=io.imread(imgLoc)
	imgray=color.rgb2gray(img)
	edge=canny(imgray)
	#show_img(rescale(edge,0.5))
	print edge.shape
	show_img(edge)
	print "edge found"
	s = [[1,1,1],[1,1,1],[1,1,1]]
	labeled_array,num_features=label(imgray,structure=s)
	print "labeling done"
	temp=[]
	print "started with",num_features,"connected components"
	for i in range(1,num_features+1):
		label_i_indices = [(labeled_array == i).nonzero()]
		if getBoundingBoxfromPixels(label_i_indices,(img.shape[1],img.shape[0])):
			temp.append(getBoundingBoxfromPixels(label_i_indices,(img.shape[1],img.shape[0])))
			
	print "started with",len(temp),"bounding boxes"
        
	interimBoundingboxes=list(temp)
	##this can be optimized later
	for item1 in temp:
		for item2 in temp:
			if (item1!=item2):
				if boundingBoxiConsumesjSpecial(item1,item2,(img.shape[1],img.shape[0])):
				#if boundingBoxiConsumedbyj(item1,item2):
					try:
						interimBoundingboxes.remove(item1)
					except ValueError:
						print "this box is already removed" 

	print "intermediately have",len(interimBoundingboxes),"bounding boxes"
	finalBoundingboxes=list(interimBoundingboxes)
	'''
	##this can be optimized later
	for item1 in interimBoundingboxes:
		for item2 in interimBoundingboxes:
			if (item1!=item2):
				result=boundingBoxiConsumedbyj(item1,item2)
				if result:
					finalBoundingboxes.remove(item1)
					break
	print "before removing small boxes",len(finalBoundingboxes),"bounding boxes"

	finalBoundingboxesFiltered=list(finalBoundingboxes)
	width=img.shape[1]
	height=img.shape[0]
	##this can be optimized later
	for item in finalBoundingboxes:
		if ((item[2]-item[0])<5) or ((item[3]-item[1])<5): 
				finalBoundingboxesFiltered.remove(item)
				
					
	print "finally have",len(finalBoundingboxesFiltered),"bounding boxes"
	
	#showing unmerged image
	pilImg=Image.fromarray(img)
	draw = ImageDraw.Draw(pilImg)
	for item in finalBoundingboxesFiltered:
		draw.rectangle([item[1],item[0],item[3],item[2]],outline="red")
	pilImg.show()
	#pilImg.save(os.path.join(imgDir,"cc",exactImageLoc))
	
	mybnumbers=0
	for item in finalBoundingboxesFiltered:
		thisarea=(item[2]-item[0])*(item[3]-item[1])
		thisareamin=min((item[2]-item[0]),(item[3]-item[1]))
		mybnumbers+=(thisareamin-5)*thisarea
		
	orgboxes=img.shape[1]*img.shape[0]*(min(img.shape[0],img.shape[1])-5)
	print "original number of boxes",orgboxes,"my boxes",mybnumbers,"ratio",mybnumbers/orgboxes
	
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
			if rectmanDist(item1,item2)<5:
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
		print i,len(label_i_indices[0][0])
		if len(label_i_indices[0][0])>0:
			temp.append(getBoundingBoxfromPixelsLarge(label_i_indices,(img.shape[1],img.shape[0])))
			

	print "after merging boundingboxes",len(temp)

	interimBoundingboxes=list(temp)
	finalBoundingboxes=list(interimBoundingboxes)
	##this can be optimized later
	for item1 in interimBoundingboxes:
		for item2 in interimBoundingboxes:
			if (item1!=item2):
				result=boundingBoxiConsumedbyj(item1,item2)
				if result:
					finalBoundingboxes.remove(item1)
					break
	print "this is final for now",len(finalBoundingboxes),"bounding boxes"
        '''
        #finalBoundingboxes=temp
	pilImg=Image.fromarray(img)
	draw = ImageDraw.Draw(pilImg)
	for item in finalBoundingboxes:
		draw.rectangle([item[1],item[0],item[3],item[2]],outline="red")
	pilImg.show()
	#pilImg.save(os.path.join(imgDir,"ccmerged",exactImageLoc))
	'''
	mybnumbers=0
	for item in finalBoundingboxes:
		thisarea=(item[2]-item[0])*(item[3]-item[1])
		thisareamin=min((item[2]-item[0]),(item[3]-item[1]))
		mybnumbers+=(thisareamin-5)*thisarea
		
	orgboxes=img.shape[1]*img.shape[0]*(min(img.shape[0],img.shape[1])-5)
	print "original number of boxes",orgboxes,"my boxes",mybnumbers,"ratio",mybnumbers/orgboxes
	
	
	boxLoc=imgLoc[:-4]+".box"
	f=open(boxLoc,"w")
	for item in finalBoundingboxesFiltered:
		f.write(str(item)+"\n")
	f.close()
	'''	
	

if __name__ == "__main__":
	main()


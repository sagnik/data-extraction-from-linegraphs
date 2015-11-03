import os,sys
from PIL import Image,ImageDraw
import numpy as np
import scipy as sp
from skimage import io,color
from matplotlib import pyplot
from scipy import stats
from pprint import pprint
from copy import deepcopy

HORIZONTALTHRESHOLD=1000
VERTICALTHRESHOLD=1000

def getBoundingBoxfromPixelsLarge(indices):
        b=[min(indices[0][0]),min(indices[0][1]),max(indices[0][0]),max(indices[0][1])] #x1,y1,x2,y2
	return b

def boundingBoxiConsumedbyj(b1,b2):
	if b1[0]>=b2[0] and b1[2]<=b2[2] and b1[1]>=b2[1] and b1[3]<=b2[3]:
		#print "true"
		return True
	else:
		return False

def iswithintenpercent(box,imgwidth):
	if box[1]<0.05*imgwidth:
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

def rectmanDistVertical(Q,R):

	box1=Q
	box2=R

	xOverlap=max(0,min(box1[2],box2[2])-max(box1[0],box2[0])) 
	yOverlap=max(0,min(box1[3],box2[3])-max(box1[1],box2[1]))
	
	if (xOverlap*yOverlap)>0:
		#print "overlap found"
		return True
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
	if (dY1+dY2)<2: #horizontal distance is very short between the rectangles
		if (dX1+dX2)<VERTICALTHRESHOLD:
			return True
	else:
		return False

def rectmanDistHorizontal(Q,R,imgwidth):

	box1=Q
	box2=R
	#if one of the boxes are within 10% from the left, use vertical merging
	#else use horizontal merging.  
	if iswithintenpercent(Q,imgwidth) or iswithintenpercent(R,imgwidth):
		#print "yes",Q
		return rectmanDistVertical(Q,R)
	xOverlap=max(0,min(box1[2],box2[2])-max(box1[0],box2[0])) 
	yOverlap=max(0,min(box1[3],box2[3])-max(box1[1],box2[1]))
	
	if (xOverlap*yOverlap)>0:
		#print "overlap found"
		return True
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
	if (dX1+dX2)<2: #vertical distance is very short between the rectangles
		if (dY1+dY2)<HORIZONTALTHRESHOLD:
			return True
	else:
		return False

def getDistHorizontal(Q,R):
	box1=Q
	box2=R
	xOverlap=max(0,min(box1[2],box2[2])-max(box1[0],box2[0])) 
	yOverlap=max(0,min(box1[3],box2[3])-max(box1[1],box2[1]))
	if yOverlap>0:
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
	if (dX1+dX2)<2: #vertical distance is very short between the rectangles
		return (dY1+dY2)
	else:
		return 0

def getDistVertical(Q,R):
	box1=Q
	box2=R
	xOverlap=max(0,min(box1[2],box2[2])-max(box1[0],box2[0])) 
	yOverlap=max(0,min(box1[3],box2[3])-max(box1[1],box2[1]))
	if xOverlap>0:
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
 
	if (dY1+dY2)<2: #vertical distance is very short between the rectangles
		return (dX1+dX2)
	else:
		return 0

def showHistogram(x,label):
	bins = np.linspace(min(x), max(x), 100)
	pyplot.hist(x, bins, alpha=0.5, label=label)
	pyplot.legend(loc='upper right')
	pyplot.show()

def mergeOnce(imgray,finalBoundingboxesFiltered,imgwidth):
	edges=sp.zeros(imgray.shape)
	labeldict={}
	colornumber=[0]
	nomerges=0
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
			#if rectmanDist(item1,item2)<max(HORIZONTALTHRESHOLD,VERTICALTHRESHOLD):
			if rectmanDistHorizontal(item1,item2,imgwidth):
				#print item1,"merged with",item2,"with",currentcolornumber
				nomerges+=1
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
			temp.append(getBoundingBoxfromPixelsLarge(label_i_indices))
			

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

	print "number of merges",nomerges
	return (finalBoundingboxes,nomerges)

def main():
	imageloc=sys.argv[1]
	pilImg=Image.open(imageloc).convert('RGB')
	dir,actualimage=os.path.split(imageloc)
	boxpredictedfile="/home/sagnik/linegraph-experiment-1/pngs/colorfigures/training/textextraction/"\
	+"goldstandardfortext/textpredictedhueboxlocs/"+actualimage[:-4]+"-textpredictedhue.box"
	boxtobesaved="/home/sagnik/linegraph-experiment-1/pngs/colorfigures/training/textextraction/"\
	+"goldstandardfortext/textpredictedhueboxlocs/words-multimerge/"+actualimage[:-4]+"-textpredictedhue.box"
	imagetobesaved="/home/sagnik/linegraph-experiment-1/pngs/colorfigures/training/textextraction/"\
	+"goldstandardfortext/textpredictedhueimage/words-multimerge/"+actualimage[:-4]+"-textpredictedhue.png"
	imgwidth=pilImg.size[0]
	print imgwidth,pilImg.size	
	#print im.size
	#imagedata=np.asarray(im)
	img=io.imread(imageloc)
	imgray=color.rgb2gray(img)
	#edge=canny(imgray)

	con=open(boxpredictedfile).read().split("\n")[:-1]
	finalBoundingboxesFiltered=[]
	for line in con:
		label=int(line.split(";")[2].split(":")[1])
		if label==1:
			temp=line.split(";")[0]
			thisbox=[int(x) for x in temp.split(",")]
			finalBoundingboxesFiltered.append(thisbox)
	print len(finalBoundingboxesFiltered)	
	finalBoundingboxesFilteredToDraw=deepcopy(finalBoundingboxesFiltered)
	horizontaldistances=[]
	verticaldistances=[]
	#horizontaldistdict={}
	#verticaldistdict={}	
	for i in range(0,len(finalBoundingboxesFiltered)):
		for j in range (i+1,len(finalBoundingboxesFiltered)):
			item1=finalBoundingboxesFiltered[i]
			item2=finalBoundingboxesFiltered[j]
			h=getDistHorizontal(item1,item2)
			v=getDistVertical(item1,item2)
			if h!=0:
				horizontaldistances.append(h)
				#horizontaldistdict[','.join([str(x) for x in item1])+';'+','.join([str(x) for x in item2])]=h
			if v!=0:
				verticaldistances.append(v)
				#verticaldistdict[','.join([str(x) for x in item1])+';'+','.join([str(x) for x in item2])]=v

	#showHistogram(horizontaldistances,"horizontal distances")
	#showHistogram(verticaldistances,"vertical distances")
	#print len(horizontaldistances),len(verticaldistances)
	#print sorted(horizontaldistances)
	#print sorted(verticaldistances)
	#print np.min(horizontaldistances),np.mean(horizontaldistances),np.median(horizontaldistances),stats.mode(horizontaldistances)
	#print np.min(verticaldistances),np.mean(verticaldistances),np.median(verticaldistances),stats.mode(verticaldistances)

	#pprint(horizontaldistdict)
	#pprint(verticaldistdict)	
	
	global HORIZONTALTHRESHOLD
	global VERTICALTHRESHOLD

	HORIZONTALTHRESHOLD=sorted(np.unique(horizontaldistances))[2]+1
	VERTICALTHRESHOLD=sorted(np.unique(verticaldistances))[1]+1

	#HORIZONTALTHRESHOLD=5
	#VERTICALTHRESHOLD=5

	#starting the merging process
	print HORIZONTALTHRESHOLD,VERTICALTHRESHOLD
	nomerges=1
	while(nomerges):
		(finalBoundingboxesFiltered,nomerges)=mergeOnce(imgray,finalBoundingboxesFiltered,imgwidth)	

	finalBoundingboxes=finalBoundingboxesFiltered
	#pilImg=Image.fromarray(img)
	draw = ImageDraw.Draw(pilImg)
	f=open(boxtobesaved,"w")
	#for item in finalBoundingboxesFilteredToDraw:
		#if item[1]<0.1*imgwidth:
		#draw.rectangle([item[1],item[0],item[3],item[2]],outline="blue")
	for item in finalBoundingboxes:
		mybox=[item[1]-2,item[0]-2,item[3]+2,item[2]+2]
		draw.rectangle(mybox,outline="red")
		f.write(",".join([str(x) for x in mybox])+"\n")
	
	#f.close()
	#pilImg.show()
	pilImg.save(imagetobesaved)
	

if __name__ == "__main__":
	main()

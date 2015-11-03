import json
import os,sys
from copy import deepcopy
from rtree import index
from pprint import pprint

WIDTHHEIGHTPARAM=0.1
INTERSECTAPARAM=0.4	
BOXHITINGPARAM=0.05
currentbox=[]

def is_number(s):
	try:
		float(s)
		return True
	except ValueError:
		return False

def getVerticalBoxes(thisindex,rtreeidx,imagetexts,imgheight):
	imagetext=imagetexts[thisindex]
	location=tuple(imagetext['TextBB'])
	rotation=imagetext['Rotation']
        extendedloc=tuple([location[0],location[1]-int(INTERSECTAPARAM*imgheight),location[2],location[3]+int(INTERSECTAPARAM*imgheight)])
	nns=list(rtreeidx.intersection(extendedloc))
	nns=[x for x in nns if x !=thisindex and is_number(imagetexts[x]['Text'])]
	return nns

def getHorizontalBoxes(thisindex,rtreeidx,imagetexts,imgwidth):
	imagetext=imagetexts[thisindex]
	location=tuple(imagetext['TextBB'])
	rotation=imagetext['Rotation']
        extendedloc=tuple([location[0]-int(INTERSECTAPARAM*imgwidth),location[1],location[2]+int(INTERSECTAPARAM*imgwidth),location[3]])
	nns=list(rtreeidx.intersection(extendedloc))
	knns=[x for x in nns if x !=thisindex and is_number(imagetexts[x]['Text'])]
	return nns

def getHorizontalBoxesToLeft(thisindex,rtreeidx,imagetexts,imgwidth):
	imagetext=imagetexts[thisindex]
	location=tuple(imagetext['TextBB'])
	extendedloc=tuple([0,location[1]-40,location[0],location[1]+40])
	nns=list(rtreeidx.intersection(extendedloc))
	nns=[x for x in nns if x!=thisindex]
	return len(nns)

def getVerticalBoxesBelow(thisindex,rtreeidx,imagetexts,imgheight):
	imagetext=imagetexts[thisindex]
	location=tuple(imagetext['TextBB'])
	extendedloc=tuple([location[0],location[3],location[2],imgheight])
	nns=list(rtreeidx.intersection(extendedloc))
	nns=[x for x in nns if x!=thisindex]
	return len(nns)

def getVerticalBoxesAbove(thisindex,rtreeidx,imagetexts,imgwidth):
	imagetext=imagetexts[thisindex]
	location=tuple(imagetext['TextBB'])
	extendedloc=tuple([location[0],0,location[2],location[1]])
	nns=list(rtreeidx.intersection(extendedloc))
	nns=[x for x in nns if x!=thisindex]
	#print nns
	return len(nns)

def isYaxisLabel(thisindex,rtreeidx,imagetexts,imgwidth,imgheight):
	rotation=imagetexts[thisindex]['Rotation']
	positive=0
	if rotation==3:
		positive+=1
	text=imagetexts[thisindex]['Text']
	if not is_number(text) or not is_number(text[:-1]):
		positive+=1
	if getHorizontalBoxesToLeft(thisindex,rtreeidx,imagetexts,imgwidth)==0:
		positive+=1
	if positive>=2:
		return True
	return False

def isXaxisLabel(thisindex,rtreeidx,imagetexts,imgwidth,imgheight):
	rotation=imagetexts[thisindex]['Rotation']
	positive=0
	if rotation==0:
		positive+=1
	text=imagetexts[thisindex]['Text']
	if not is_number(text) or not is_number(text[:-1]):
		positive+=1
	if getVerticalBoxesBelow(thisindex,rtreeidx,imagetexts,imgheight)==0:
		positive+=1
	if positive==3:
		return True
	return False

#we will return a confidence level of 1 and 2 with the x-axis and y-axis values
#if the confidence is high, we don't change it to legend. 
def isYaxisValue(thisindex,rtreeidx,imagetexts,imgwidth,imgheight):
	nns=getVerticalBoxes(thisindex,rtreeidx,imagetexts,imgheight)
	text=imagetexts[thisindex]['Text']
	location=imagetexts[thisindex]['TextBB']
	if not is_number(text):
		return (False,0)
	if len(nns)<2:
		return (False,0)
	else:	#should we handle this better?
		if location[0]<WIDTHHEIGHTPARAM*imgwidth:
			return (True,2)
		else:
			return (True,1)
	
def isXaxisValue(thisindex,rtreeidx,imagetexts,imgwidth,imgheight):
	nns=getHorizontalBoxes(thisindex,rtreeidx,imagetexts,imgwidth)
	text=imagetexts[thisindex]['Text']
	location=imagetexts[thisindex]['TextBB']
	if not is_number(text):
		return (False,0)
	if len(nns)<2:
		return (False,0)
	else:	#should we handle this better?
		if imgheight-location[3]<WIDTHHEIGHTPARAM*imgheight:
			return (True,len(nns)+1)
		else:
			return (True,len(nns))

def isFigureLabel(thisindex,rtreeidx,imagetexts,imgwidth,imgheight):
	#print "here"
	location=imagetexts[thisindex]['TextBB']
	if getVerticalBoxesAbove(thisindex,rtreeidx,imagetexts,imgwidth)==0 and location[1]<WIDTHHEIGHTPARAM*imgheight:
		return True
	else:
		return False
 	
def getClass(thisindex,rtreeidx,imagetexts,imgwidth,imgheight):
	#print "here"
	if isYaxisValue(thisindex,rtreeidx,imagetexts,imgwidth,imgheight)[0]:
		#print thisindex, "returned","yaxisvalue"
		#print "yaxisvalue:"+str(isYaxisValue(thisindex,rtreeidx,imagetexts,imgwidth,imgheight)[1])
		return ("yaxisvalue",isYaxisValue(thisindex,rtreeidx,imagetexts,imgwidth,imgheight)[1])
	if isXaxisValue(thisindex,rtreeidx,imagetexts,imgwidth,imgheight)[0]:
		#print thisindex, "returned","xaxisvalue"
		return ("xaxisvalue",isXaxisValue(thisindex,rtreeidx,imagetexts,imgwidth,imgheight)[1])
	if isYaxisLabel(thisindex,rtreeidx,imagetexts,imgwidth,imgheight):
		#print thisindex, "returned","yaxislabel"
		return ("yaxislabel",3)
	if isXaxisLabel(thisindex,rtreeidx,imagetexts,imgwidth,imgheight):
		#print thisindex, "returned","xaxislabel"
		return ("xaxislabel",1)
	if isFigureLabel(thisindex,rtreeidx,imagetexts,imgwidth,imgheight):
		#print thisindex, "returned","figurelabel"
		return ("figurelabel",1)
	return ("undefined",1)	

def relabelUndefinedStep1(thisindex,rtreeidx,imagetexts,imgwidth,imgheight):
	#the algorithm is as follows:
	#we increase the box by 5%, see if intersects with other blocks.
	# if doesn't return undefined.
	# if the one of the intersecting boxes have labels X-axis-value, Y-axis-value
	# or y-axis label, return undefined, else, return the intersecting boxes 
	# and make them undefined in the calling function.   
	location=imagetexts[thisindex]['TextBB']
	extendedloc=tuple([location[0]-BOXHITINGPARAM*imgwidth,location[1]-BOXHITINGPARAM*imgheight,\
	location[2]+BOXHITINGPARAM*imgwidth,location[3]+BOXHITINGPARAM*imgheight])
	nns=list(rtreeidx.intersection(extendedloc))
	nns=[x for x in nns if x!=thisindex]
	#if nns:
	#	print "hit",imagetexts[thisindex]['Text'],[imagetexts[x]['Text'] for x in nns]
	adjacentlabels=[imagetexts[x]['TextLabel'] for x in nns]
	#print "adjacentlables",adjacentlabels
	if 'xaxisvalue' in adjacentlabels or 'yaxisvalue' in adjacentlabels or 'yaxislabel' in adjacentlabels:
		return ["undefined"]
	else:
		return nns 

def mergeBoxes(existing,nns,imagetexts):
	#print "yes",existing,nns,imagetexts[nns[0]]['TextBB'][0]
	x1s=[imagetexts[i]['TextBB'][0] for i in nns]
	x1s.append(existing[0])
	y1s=[imagetexts[i]['TextBB'][1] for i in nns]
	y1s.append(existing[1])
	x2s=[imagetexts[i]['TextBB'][2] for i in nns]
	x2s.append(existing[2])
	y2s=[imagetexts[i]['TextBB'][3] for i in nns]
	y2s.append(existing[3])
	#print x1s,y1s,x2s,y2s
	return [min(x1s),min(y1s),max(x2s),max(y2s)]

def relabelUndefinedStep2(thisindex,rtreeidx,imagetexts,imgwidth,imgheight):
	#we take an undefined box, increase it by 5%,
        #if we do not hit anything, we return a null list
	#if we hit any box, we change it's label to legend. 
	# and change the current box to include the changes box. initially 
        #the currentbox is empty
	global currentbox
	location=imagetexts[thisindex]['TextBB']
	if not currentbox:
		extendedloc=tuple([location[0]-BOXHITINGPARAM*imgwidth,location[1]-BOXHITINGPARAM*imgheight,\
		location[2]+BOXHITINGPARAM*imgwidth,location[3]+BOXHITINGPARAM*imgheight])
	else:
		extendedloc=tuple([currentbox[0]-BOXHITINGPARAM*imgwidth,currentbox[1]-BOXHITINGPARAM*imgheight,\
		currentbox[2]+BOXHITINGPARAM*imgwidth,currentbox[3]+BOXHITINGPARAM*imgheight])
	nns=list(rtreeidx.intersection(extendedloc))
	'''
	newnns=[]
	for x in nns:
		if x==thisindex:
			continue
		elif imagetexts[x]['TextLabel']=='xaxisvalue' and (imgheight-imagetexts[x]['TextBB'][3])<WIDTHHEIGHTPARAM*imgheight:
			continue
		elif imagetexts[x]['TextLabel']=='yaxisvalue' and imagetexts[x]['TextBB'][0]<WIDTHHEIGHTPARAM*imgwidth:
			continue
		else:
			newnns.append(x)
 	nns=newnns
	'''
	#confirmedlabels=["xaxisvalue","yaxisvalue","yaxislabel"]
	#print nns,":",[x for x in nns if imagetexts[x]['TextLabel'] in confirmedlabels]
	#print nns
	nns=[x for x in nns if x!=thisindex and not imagetexts[x]['TextLabelConf']>=3] #right now, only xaxisvalue, yaxisvalue and yaxislabel 		can be 2, so not checking for the labels anymore 
	#print thisindex,nns,currentbox
	#print nns
	if not nns:
		return "undefined"
	
	if not currentbox:
		currentbox=mergeBoxes(location,nns,imagetexts)
	else: #currentbox already exists	
		currentbox=mergeBoxes(currentbox,nns,imagetexts)
	return "processed"	

 
def main():
	jsonfile=sys.argv[1]
	direc,actjsonfile=os.path.split(jsonfile)
	modjsonloc=os.path.join("jsonsimagetextclasspredicted",actjsonfile[:-5]+"-imagetextclasspredicted.json")
	content=json.load(open(jsonfile,"r"))
	con=deepcopy(content)		
	imagetexts=con['ImageText']
	rtreeidx=index.Index()
	rtreeidxvrt=index.Index()
	rtreeidxhorz=index.Index()
	imgbb=con['ImageBB']
	imgwidth=2*(imgbb[2]-imgbb[0])
	imgheight=2*(imgbb[3]-imgbb[1])
	
	for ind,imagetext in enumerate(imagetexts):
		rtreeidx.insert(ind,tuple(imagetext['TextBB']))

	for ind,imagetext in enumerate(imagetexts):
		#print ind,imagetext['Text'],imagetext['TextBB'],getClass(ind,rtreeidx,imagetexts,imgwidth,imgheight)
		textlabelconf=getClass(ind,rtreeidx,imagetexts,imgwidth,imgheight)
		con['ImageText'][ind]['TextLabel']=textlabelconf[0]
		con['ImageText'][ind]['TextLabelConf']=textlabelconf[1]	
	
	#relabel undefined boxes
	imagetexts=con['ImageText']
	for ind,imagetext in enumerate(imagetexts):
		#print ind,imagetext['Text'],imagetext['TextBB'],getClass(ind,rtreeidx,imagetexts,imgwidth,imgheight)
		textlabel=con['ImageText'][ind]['TextLabel'][0]
		if textlabel=="undefined":
			output=relabelUndefinedStep1(ind,rtreeidx,imagetexts,imgwidth,imgheight)
			if output:
				if output[0]!="undefined":
					for item in output:
						con['ImageText'][item]['TextLabel']="undefined"
						con['ImageText'][item]['TextLabelConf']=1

	imagetexts=con['ImageText']
	#pprint(con)

	for ind,imagetext in enumerate(imagetexts):
		#print ind,imagetext['Text'],imagetext['TextBB'],getClass(ind,rtreeidx,imagetexts,imgwidth,imgheight)
		textlabel=con['ImageText'][ind]['TextLabel']
		if textlabel=="undefined":
			output=relabelUndefinedStep2(ind,rtreeidx,imagetexts,imgwidth,imgheight)
	if currentbox:
		currentboxintersects=list(rtreeidx.intersection(tuple(currentbox)))
		for item in currentboxintersects:
			con['ImageText'][item]['TextLabel']="legend"
			con['ImageText'][item]['TextLabelConf']=1	
	
	json.dump(con,open(modjsonloc,"w")) 
	
if __name__=="__main__":
	main()

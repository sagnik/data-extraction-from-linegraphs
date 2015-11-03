import json
import os,sys
from copy import deepcopy
from rtree import index
'''
def test(thisindex,rtreeidx,imagetexts):
	imagetext=imagetexts[thisindex]
	location=tuple(imagetext['TextBB'])
	rotation=imagetext['Rotation']
	print "original text",imagetext['Text']
	nns=list(rtreeidx.nearest(location, 3))
	for n in nns:
		print n,imagetexts[n]['Text']
'''
WIDTHHEIGHTPARAM=0.4
INTERSECTAPARAM=0.2	
def is_number(s):
	try:
		float(s)
		return True
	except ValueError:
		return False

def getVerticalNumbers(thisindex,rtreeidx,imagetexts,imgheight):
	imagetext=imagetexts[thisindex]
	location=tuple(imagetext['TextBB'])
	rotation=imagetext['Rotation']
	#print "original text",imagetext['Text']
        extendedloc=tuple([location[0],location[1]-int(INTERSECTAPARAM*imgheight),location[2],location[3]+int(INTERSECTAPARAM*imgheight)])
	nns=list(rtreeidx.intersection(extendedloc))
	#print nns
	noverticalnumbers=0
	#print "extendedloc",extendedloc,"nnslen",len(nns)
	for n in nns:
		if n!=thisindex:
			if is_number(imagetexts[n]['Text']):
				noverticalnumbers+=1
	return noverticalnumbers

def getHorizontalNumbers(thisindex,rtreeidx,imagetexts,imgwidth):
	imagetext=imagetexts[thisindex]
	location=tuple(imagetext['TextBB'])
	rotation=imagetext['Rotation']
	#print "original text",imagetext['Text']
        extendedloc=tuple([location[0]-int(INTERSECTAPARAM*imgwidth),location[1],location[2]+int(INTERSECTAPARAM*imgwidth),location[3]])
	nns=list(rtreeidx.intersection(extendedloc))
	#print nns
	nohorizontalnumbers=0
	for n in nns:
		if n!=thisindex:
			if is_number(imagetexts[n]['Text']):
				nohorizontalnumbers+=1
	return nohorizontalnumbers

def getClass(thisindex,rtreeidx,imagetexts,imgwidth,imgheight):
	#check if it is Y-axis value
	# is it a number?
	imagetext=imagetexts[thisindex]
	rotation=imagetext['Rotation']
	if rotation==3:
		return 'yaxislabel'
	if not is_number(imagetext['Text']):
		return "undefined"
		#check later whether legend, axis text
	else:#it's a number, can have any of the labels, 
		verticalnumbers=getVerticalNumbers(thisindex,rtreeidx,imagetexts,imgheight)
		horizontalnumbers=getHorizontalNumbers(thisindex,rtreeidx,imagetexts,imgwidth)
		#print verticalnumbers,horizontalnumbers
		if verticalnumbers>=horizontalnumbers and imagetext['TextBB'][0]<WIDTHHEIGHTPARAM*imgwidth:
			return "yaxisvalue"
		elif horizontalnumbers>=verticalnumbers and imgheight-imagetext['TextBB'][3]<WIDTHHEIGHTPARAM*imgheight:
			return "xaxisvalue"
		else:
			return "undefined"
			
	##check if it is X-axis value		

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
	imgwidth=imgbb[2]-imgbb[0]
	imgheight=imgbb[3]-imgbb[1]
	
	for ind,imagetext in enumerate(imagetexts):
		rtreeidx.insert(ind,tuple(imagetext['TextBB']))
		#bb=imagetext['TextBB']
		#rtreeidxvrt.insert(ind,tuple([0,bb[1],0,bb[3]]))
		#rtreeidxhorz.insert(ind,tuple([bb[0],0,bb[2],0]))
	#should we change bbox, according to the r-tree protocol
	#http://toblerity.org/rtree/tutorial.html#creating-an-index
	#(left, bottom, right, top)
	for ind,imagetext in enumerate(imagetexts):
		#print ind,imagetext['Text'],imagetext['TextBB'],getClass(ind,rtreeidx,imagetexts,imgwidth,imgheight)
		textlabel=getClass(ind,rtreeidx,imagetexts,imgwidth,imgheight)
		con['ImageText'][ind]['TextLabel']=textlabel	
	'''	
	for index,imagetext enumerate(imagetexts):
		con['ImageText'][index]=getClass(imagetext,index,imagetexts)
	'''
	json.dump(con,open(modjsonloc,"w")) 
	
if __name__=="__main__":
	main()

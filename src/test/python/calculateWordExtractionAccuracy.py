from __future__ import division
from rtree import index as index
import sys
import json
import os

def findOverLap(box1,box2):
	xOverlap=max(0,min(box1[2],box2[2])-max(box1[0],box2[0])) 
	yOverlap=max(0,min(box1[3],box2[3])-max(box1[1],box2[1]))
	return xOverlap*yOverlap
	
def main():
	predictedf=sys.argv[1]
	predictedfdict=predictedf[:-4]+"-predictedgoldmatched.dict"
	predictdir,actpredictf=os.path.split(predictedf)
	goldf="/home/sagnik/data/linegraph-data/modjsons/"+actpredictf[:-18]+".json"
	#dir,actgoldf=os.path.split(goldf)
	goldboxesall=json.load(open(goldf))['ImageText']
	goldboxes=[x['TextBB'] for x in goldboxesall]
	if len(goldboxes)==0:
		print "sorry, no gold standard for evaluation"
		return
	#predicteddir=
	#predictedf=os.path.join(predicteddir,actgoldf[:-5]+"-wordpredicted.box"
	predictedboxes=[]
	for line in open(predictedf).read().split("\n")[:-1]:
		box=[int(x) for x in line.split(",")]
		predictedboxes.append([box[1],box[0],box[3],box[2]])
	
	#print predictedboxes
	rtreeidx=index.Index()
	for ind,predictedbox in enumerate(predictedboxes):
		rtreeidx.insert(ind,predictedbox)
	

	#EASIER EVALUATION METHOD, MORE STRINGENT
	#----------------------------------------
	#1. R_OB=no. of correctly identified rectangles/no. of rectangles in ground truth
	#2. P_OB=no. of correctly identified rectangles/no. of rectangles predicted
	#3. correctly identified recatngle=AreaPrecision>0.4,AreaRecall>0.8
	#4. AreaRecall=Overlap of two rectangles/Area of ground truth box
	#5. AreaPrecision=Overlap of two rectangles/Area of predicted box
 
	#ICDAR EVALUATION ALGORITHM
	#------------------------------
	#1. G is ground truth, which has i boxes
	#2. D is predicted truth, which has j boxes
	#3. create two matrices AreaPrecision[i,j] and AreaRecall[i,j]
	#4. AreaPrecision[i,j]=AreaPrecision(G_i,D_j) 
	#5. AreaRecall[i,j]=AreaRecall(G_i,D_j) 
	#5. R_OB(G, D, t_r, t_p)=Sum(Match_G(G_i, D, t_r, t_p))/|G|
	#6. P_OB(G, D, t_r, t_p)=Sum(Match_D(G, D_j, t_r, t_p))/|D|
	# for more, read (http://liris.cnrs.fr/Documents/Liris-2216.pdf)
	# going with the easier method now.
	
	#notfoundgoldboxes=[]
	#unusedpredictedboxes=[]
	noofmatches=0
	matchesdict={}
	#alreadyfound=[]
	for goldbox in goldboxes:
		#print goldbox
		#for all boxes that intersects with this box, find out the one
		#having maximum overlap.
		#calculate AreaPrecision and AreaRecall for that box
		#if AreaPrecision > 0.4 and AreaRecall > 0.8, we say it's match
		nns=list(rtreeidx.intersection(tuple(goldbox)))
		maxOverlap=0
		maxOverlapindex=-1
		
		for ind in nns:
			overlappingpredictedbox=predictedboxes[ind]
			overlap=findOverLap(goldbox,overlappingpredictedbox)
			if overlap>maxOverlap:
				maxOverlap=overlap
				maxOverlapindex=ind
		
		truebox=predictedboxes[maxOverlapindex]
		AreaPrecision=maxOverlap/((truebox[2]-truebox[0])*(truebox[3]-truebox[1]))
		AreaRecall=maxOverlap/((goldbox[2]-goldbox[0])*(goldbox[3]-goldbox[1]))
		if AreaPrecision>0.4 and AreaRecall>0.4:
			#print "we found a match"
			if ','.join([str(x) for x in truebox]) not in matchesdict:
				matchesdict[','.join([str(x) for x in truebox])]=[]
				matchesdict[','.join([str(x) for x in truebox])].append(goldbox)
				noofmatches+=1
			else:
				print "the box was already there"
				matchesdict[','.join([str(x) for x in truebox])].append(goldbox)
	
	R_OB=(noofmatches/len(goldboxes))*100
	P_OB=(noofmatches/len(predictedboxes))*100
	matchesdict['R_OB']=R_OB
	matchesdict['P_OB']=P_OB
	json.dump(matchesdict,open(predictedfdict,"wb"))
	print "recall",R_OB,"precision",P_OB


if __name__=="__main__"	:
	main()			 	

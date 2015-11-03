import os
import sys
from sklearn import metrics

predictedresultsdir="/home/sagnik/linegraph-experiment-1/pngs/colorfigures/training/textextraction/goldstandardfortext/textpredictedhueboxlocs/"

goldlabels=[]
predictedlabels=[]

predictedfiles=[x for x in os.listdir(predictedresultsdir) if x.endswith("box")]
for pf in predictedfiles:
	con=open(predictedresultsdir+pf).read().split("\n")[:-1]
	for line in con:
		gl=int(line.split(";")[1])
		pl=int(line.split(";")[2].split(":")[1])
		if gl!=pl:	
			print pf,line.split(";")[0]
		goldlabels.append(gl)
		predictedlabels.append(pl)
	#print pf

print "precision",metrics.precision_score(goldlabels,predictedlabels)
print "recall",metrics.recall_score(goldlabels,predictedlabels)	
print "f1-score",metrics.f1_score(goldlabels,predictedlabels)


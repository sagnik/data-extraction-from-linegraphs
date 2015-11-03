import sys
import json

goldboxes=json.load(open(sys.argv[1]))['ImageText']
predictedboxes=#something
for box in predictedboxes:
	predictedbox=[box[1],box[0],box[3],box[2]]
	

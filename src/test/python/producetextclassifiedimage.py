import os,sys
from PIL import Image,ImageDraw
import json

def drawRectangle(draw,textbb,labelcolor):
	#draw.rectangle(draw,textbb,outline=labelcolor)
	for x in range(1,-2,-1):
		draw.rectangle(((textbb[0]-x,textbb[1]-x),(textbb[2]+x,textbb[3]+x)),outline=labelcolor)

def main():
	colordict={
	'xaxisvalue':(0,0,255),
        'yaxisvalue':(0,255,0),
	'xaxislabel':(242,238,102),
	'yaxislabel':(255,51,204),
	'figurelabel':(102,240,242),
	'legend':(0,0,0),
	'undefined':(255,0,0)
        }
	imgFile=sys.argv[1]
	modimgFile=imgFile[:-4]+"-textclassified.png"
	jsonfile=os.path.join("jsonsimagetextclasspredicted",os.path.split(imgFile)[1][:-4]+"-imagetextclasspredicted.json")
	jc=json.load(open(jsonfile))
	imagetexts=jc['ImageText']
	im=Image.open(imgFile).convert('RGB')
	draw=ImageDraw.Draw(im)
	for index,imagetext in enumerate(imagetexts):
		textbb=imagetext['TextBB']
		print textbb,type(textbb)
		labelcolor=colordict[imagetext['TextLabel']]
		drawRectangle(draw,textbb,labelcolor)
	im.save(modimgFile)	
	
if __name__=="__main__":
	main()	 

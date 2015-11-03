import web
import sys,os,shutil
import json 
import csv

jsondir='/home/sagnik/linegraph-experiment-1/jsonsimagetextclasspredicted/'#sys.argv[1]
imagedir='/home/sagnik/linegraph-experiment-1/pngs/colorfigures/training/'#sys.argv[2]
jsons=[os.path.join(jsondir,x) for x in os.listdir(jsondir) if "imagetextclasspredicted.json" in x]
jsons=[x for x in jsons if 'GoldLabelsTagged' not in json.load(open(x))]
currentindex=0
render = web.template.render('templates/')
urls = (
    '/', 'index'
)

class index: 
    def GET(self):
        jsondir,jsonfile=os.path.split(jsons[currentindex])
        imgloc=os.path.join(imagedir,jsonfile[:-29]+"-textclassified.png")
        shutil.copy(imgloc,"static")
	print "currentindex get",currentindex,jsons[currentindex]
        unlabeledimtext=json.load(open(jsons[currentindex]))['ImageText']
        for index,item in enumerate(unlabeledimtext):
            unlabeledimtext[index]['TextLabelGold']='textlabelgold-'+unlabeledimtext[index]['TextLabel']	
	
        return render.test2(json.dumps(unlabeledimtext),jsonfile[:-29]+"-textclassified.png")
     
    def POST(self):
        inputdata=web.input()
        global currentindex
        currentjson=json.load(open(jsons[currentindex]))
        try:
            for item in inputdata.keys():
                currentjson['ImageText'][int(item)]['TextLabelGold']=inputdata[item]
            currentjson['GoldLabelsTagged']=True
            json.dump(currentjson,open(jsons[currentindex],"wb"))
            currentindex+=1
            print "success",currentindex
        except (KeyError,IOError,IndexError): 
            print "something wronng happened"
	
        jsondir,jsonfile=os.path.split(jsons[currentindex])
        imgloc=os.path.join(imagedir,jsonfile[:-29]+"-textclassified.png")
        shutil.copy(imgloc,"static")
        unlabeledimtext=json.load(open(jsons[currentindex]))['ImageText']
        for index,item in enumerate(unlabeledimtext):
            unlabeledimtext[index]['TextLabelGold']='textlabelgold-'+unlabeledimtext[index]['TextLabel']	
	
        return render.test2(json.dumps(unlabeledimtext),jsonfile[:-29]+"-textclassified.png")

if __name__=="__main__":
    web.internalerror = web.debugerror
    app = web.application(urls, globals())
    app.run()



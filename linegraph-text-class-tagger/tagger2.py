import web
import sys,os,shutil
import simplejson as json 
import csv

jsondir='/home/sagnik/linegraph-experiment-1/jsonsimagetextclasspredicted/'#sys.argv[1]
imagedir='/home/sagnik/linegraph-experiment-1/pngs/colorfigures/training/'#sys.argv[2]
jsons=[os.path.join(jsondir,x) for x in os.listdir(jsondir) if "imagetextclasspredicted.json" in x]
jsons=[x for x in jsons if 'GoldLabelsTagged' not in json.load(open(x)) or not json.load(open(x))['GoldLabelsTagged']]
currentindex=0
currentmaxindex=len(jsons)

render = web.template.render('templates/')
urls = (
    '/', 'index'
)
wrongfiles=open("wrongfilescouldnttag","a")
class index: 
    def GET(self):
        if currentindex==currentmaxindex:
            return "Tagging finished"
        jsondir,jsonfile=os.path.split(jsons[currentindex])
        imgloc=os.path.join(imagedir,jsonfile[:-29]+"-textclassified.png")
        shutil.copy(imgloc,"static")
        print "currentindex get",currentindex,jsons[currentindex]
        unlabeledimtext=json.load(open(jsons[currentindex]))['ImageText']
        for index,item in enumerate(unlabeledimtext):
            unlabeledimtext[index]['TextLabelGold']=unlabeledimtext[index]['TextLabel']	
        imgbb=json.load(open(jsons[currentindex]))['ImageBB']
        imgwidth=(imgbb[2]-imgbb[0])*2
        imgheight=(imgbb[3]-imgbb[1])*2
        return render.jslabeltagging2(json.dumps(unlabeledimtext),jsonfile[:-29]+"-textclassified.png",\
        str(imgwidth)+"px",str(imgheight)+"px")
     
    def POST(self):
        inputdata=web.input()
        print inputdata
        global currentindex
        currentjson=json.load(open(jsons[currentindex]))
        try:
            #unlabeledimtext=['ImageText']
            for index,item in enumerate(currentjson['ImageText']):
                currentjson['ImageText'][index]['TextLabelGold']=currentjson['ImageText'][index]['TextLabel']
            if 'submitwrong' in inputdata.keys():
                currentjson['GoldLabelsTagged']=True
                currentjson['SomethingWrong']=True
                json.dump(currentjson,open(jsons[currentindex],"wb"))
                currentindex+=1
                print "failure",currentindex
                wrongfiles.write(jsons[currentindex]+"\n")
                	
            else:
                for item in inputdata.keys():
                    currentjson['ImageText'][int(item)]['TextLabelGold']=inputdata[item]
            
                currentjson['GoldLabelsTagged']=True
                json.dump(currentjson,open(jsons[currentindex],"wb"))
                currentindex+=1
                print "success",currentindex
        except (KeyError,IOError,IndexError): 
            print "something wronng happened"
            wrongfiles.write(jsons[currentindex]+"\n")
            currentindex+=1
            return
	return

        
if __name__=="__main__":
    web.internalerror = web.debugerror
    app = web.application(urls, globals())
    app.run()



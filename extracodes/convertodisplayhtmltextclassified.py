bastring="<!DOCTYPE html>\n<html>\n<body>\n<h2>Images</h2><h3>Color code</h3>"
bastring+='<p><span style="color:rgb(0,0,255);font-size:20px">X-axis value</span></p>'
bastring+='<p><span style="color:rgb(0,255,0);font-size:20px">Y-axis value</span></p>'
bastring+='<p><span style="color:rgb(242,238,102);font-size:20px">X-axis label</span></p>'
bastring+='<p><span style="color:rgb(255,51,204);font-size:20px">Y-axis label</span></p>'
bastring+='<p><span style="color:rgb(102,240,242);font-size:20px">Figure label</span></p>'
bastring+='<p><span style="color:rgb(0,0,0);font-size:20px">Legend</span></p>'
bastring+='<p><span style="color:rgb(255,0,0);font-size:20px">Not classified yet</span></p>'
endstring="</body>\n</html>"
contentloc="predictedbasecolors-h1"
filelocs=open(contentloc,"r").read().split("\n")[:-1]
image=""
for line in filelocs:
	image+='\n<p> <img src="'+line.split(",")[0]+'" style="width:500px;height:350px" border="5"> <img src="'+\
	line.split(",")[0][:-4]+'-textclassified.png'\
	+'" style="width:500px;height:350px" border="5"> <span style="color:blue font-size:20px">'+line.split(",")[1]+'</span>'+line.split(",")[0]+'</p>\n'

with open("displaytextclassified.html","w") as f:
	f.write(bastring+image+endstring)
	

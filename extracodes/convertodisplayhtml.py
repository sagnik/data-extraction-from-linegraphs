bastring="<!DOCTYPE html>\n<html>\n<body>\n<h2>Images</h2>"
endstring="</body>\n</html>"
contentloc="predictedbasecolors-h1"
filelocs=open(contentloc,"r").read().split("\n")[:-1]
image=""
for line in filelocs:
	image+='\n<p> <img src="'+line.split(",")[0]+'" style="width:500px;height:350px" border="5"> <img src="'+\
	line.split(",")[0][:-4]+'-textclassified.png'\
	+'" style="width:500px;height:350px" border="5"> <span style="color:blue font-size:20px">'+line.split(",")[1]+'</span> </p>\n'

with open("displaytextclassified.html","w") as f:
	f.write(bastring+image+endstring)
	

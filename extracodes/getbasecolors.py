from skimage import io, color
from PIL import Image
import numpy as np
from colormath.color_objects import LabColor, sRGBColor
from colormath.color_conversions import convert_color
from colormath.color_diff import delta_e_cie1976
from skimage.color import lab2rgb
from matplotlib import pyplot as plt

def show_img(img):
	width = img.shape[1]/75.0
	height = img.shape[0]*width/img.shape[1]
	f = plt.figure(figsize=(width, height))
	plt.imshow(img)
	plt.show()

colorthreshold=100

def findNearestColor(thiscolor,x,y):
 minDist=10000
 global colordict
 mincolor=[0,0,0]
 for item in colordict.keys():
  testcolorlist=[float(i) for i in item.split(',')]
  cl1=LabColor(testcolorlist[0],testcolorlist[1],testcolorlist[2])
  cl2=LabColor(thiscolor[0],thiscolor[1],thiscolor[2])
  dist=delta_e_cie1976(cl1,cl2)
  if dist<minDist:
   minDist=dist
   mincolor=np.array(testcolorlist)

 if minDist<colorthreshold:
  colordict[item].append((x,y)) 
  return mincolor
 else:
  keylist=[str(i) for i in list(thiscolor)]
  colordict[','.join(keylist)]=[(x,y)]
  return None

#img=Image.open('pngs/10.1.1.186.3729-Figure-5-mod.png').convert('RGB')
rgb=io.imread('pngs/10.1.1.186.3729-Figure-5-mod.png')[:,:,0:3]
print rgb.shape
show_img(rgb)
lab = color.rgb2lab(rgb)
print lab.shape
colordict={}
keylist=[str(x) for x in list(lab[0][0])]
colordict[','.join(keylist)]=[(0,0)]
for x in range(1,lab.shape[0]):
 print x,len(colordict.keys())
 for y in range(0,lab.shape[1]):
  out=findNearestColor(lab[x][y],x,y)
  if out !=None:
   lab[x,y]=out

print "visibly distinguishable colors",len(colordict.keys())
rgb=lab2rgb(lab)
#Image.fromarray(rgb).show()
show_img(rgb)

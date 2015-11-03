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

'''
def getNonContiguousColors(arr):
 sL = s.tolist()
 indices = [i for i, x in enumerate(sL) if x == [0,0,0]]
'''
#1. get 10 vertical lines within 70% of the main image.
#2. for each line,
# a. get the foreground pixels (for now, assume non-white)
# b. find out contiguous chunks of of indices. 
# c. if chunk length<3, discard.
# d. find mode color of the chunk.
# e. set all colors in the chunk to the mode color in rgb. add the modecolor in LAB to the colordict as key and the pixel tuple as value. 
   
def getBaseColors():
 w=rgb.shape[0]
 h=rgb.shape[1]
 print w,h
 ys=range(int(0.15*h),int(0.85*h),10)
 for y in ys:
  print "y",y
  s=rgb[:,y]
  condition = (s[:,0]==255) & (s[:,1]==255) & (s[:,2]==255)
  nbgs=list(set(range(0,len(s))) - set(np.where(condition)[0].tolist()))
  nbgs.sort()
  print nbgs
  #item=nbgs[0]
  temp=[]
  for i in range(0,len(nbgs)-1): 
   if nbgs[i+1]==nbgs[i]+1:
    temp.append(nbgs[i])
    i=i+1
    temp.append(nbgs[i])
   else:
    #temp.append(nbgs[i+1])
    #temp=temp[:-1]
    print "group: ",list(set(temp))
    temp=[]
 #get 10 vertical lines 


rgb=io.imread('pngs/10.1.1.186.3729-Figure-5-mod.png')[:,:,0:3]
print rgb.shape
#show_img(rgb)
lab = color.rgb2lab(rgb)
getBaseColors()
'''
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

condition = (s[:,0]==255) & (s[:,1]==255) $ (s[:,2]==255)
list(set(range(0,len(s))-set(list(np.where(condition))))
 
list(set(range(0,len(s))) - set(np.where(condition)[0].tolist()))
'''



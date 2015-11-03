from PIL import Image
import numpy as np
from matplotlib import pyplot as plt
import matplotlib.cm as cm
import sys
import colorsys
from skimage.io import imread
from skimage.filters import threshold_otsu
import copy

def show_img(img1,img2):
	fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(8, 2.5))
	ax1.imshow(img1, cmap=plt.cm.gray)
	ax2.imshow(img2, cmap=plt.cm.gray)
	plt.show()

#takes an input image and divides it into blocks of 2*2. If the total for that 
def subSampling(img,threshold=1):
	tempimg=copy.deepcopy(img)
	for i in range(0,img.shape[0],2):
		for j in range(0,img.shape[1],2):
			temp=img[i:i+2,j:j+2]
			if np.sum(np.asarray(temp,dtype=np.uint8))>=threshold:
				tempimg[i:i+2,j:j+2]=True
			else:
				tempimg[i:i+2,j:j+2]=False 		
	return tempimg		

'''

(i)
an input image with foreground pixels ‘1’ and background pixels ‘0’ is used as mask image, ii) the filled-image
is initialized with all ‘0’ pixels except the top-left pixel with ‘1’, iii) the filled-image is dilated using a 3 × 3 structuring element, iv) after dilation, all of the pixels that are ‘0’ in the mask image are set to ‘0’ in the filled-image is initialized with all ‘0’ pixels except the top-left pixel with ‘1’, iii) the filled-image is dilated using a 3 × 3 structuring element, iv) after dilation, all of the pixels that are ‘0’ in the mask image are set to ‘0’ in the filled-image, v) dilation followed by resetting of the filled-image’s pixels is repeated until no more changes are made
to the filled-image. 
WHAT IS THE FUCKING INTUITION?
'''

def main():
	
	imagefile=sys.argv[1]
	image=imread(imagefile,as_grey=True)	
	thresh = threshold_otsu(image)
	binary = np.logical_not(image > thresh)
	modbinary=subSampling(subSampling(subSampling(subSampling(binary)),4),3)
	show_img(binary,modbinary)
	#print type(binary),binary.shape,binary[7][9],binary[177][538]
	#plt.imshow(binary, cmap=plt.cm.gray)
	#plt.show()
	

if __name__=="__main__":
	main()


from __future__ import division
from PIL import Image
import numpy as np
from matplotlib import pyplot as plt
import matplotlib.cm as cm
import sys
import colorsys
from skimage.io import imread
from skimage.filters import threshold_otsu
import copy

K=100
def getS(D,X):
	S=np.zeros((D.shape[1],X.shape[1]))
	for i in range(0,X.shape[1]):
		xi=X[:,i]
		maxindex=0
		maxval=0
		for j in range(0,D.shape[1]):
			dj=D[:,j]
			p=np.dot(xi,dj)
			if p>maxval:
				maxval=p
				maxindex=j
		S[maxindex][i]=maxval
	return S

def columnNormalize(D):
	temp=copy.deepcopy(D)
	
	for r in range(0,D.shape[1]):
		x=D[:,r]
		norm=np.linalg.norm(x)
		if norm==0:
			temp[:,r]=x	
		else:
			temp[:,r]=temp[:,r]/norm
			print norm,np.count_nonzero(D[:,r]),temp[:,r][0],np.count_nonzero(temp[:,r])
	return temp

def dict_learning(enfeatures):
	X=np.transpose(enfeatures) #each column is a data point now, there are 81 rows and 
	#no. of columns = no. of black pixels
	#initialization with K cluster centers (choose k cluster centers randomly)
	randomindices=np.random.randint(X.shape[1],size=100) #choose 100 cluster centers to initialize
	D=X[:,randomindices]
	
	D=columnNormalize(D)
	#print X.shape, D.shape, D[].shape[1]
	S=getS(D,X)
	print S.shape, np.count_nonzero(S[0,:])
  	
def image_featurization(image):
	#binarization
	thresh = threshold_otsu(image)
	binary = np.array(np.logical_not(image > thresh),dtype=np.uint8) #black pixels=1
	blackindices=np.nonzero(binary)
	print blackindices[0].shape
	#eight neighborhood patch
	enfeatures=[]
	for x,y in zip(blackindices[0],blackindices[1]):
		enfeatures.append(np.reshape(binary[x-4:x+5,y-4:y+5],81))
	enfeatures=dict_learning(enfeatures) 	

def main():
	imagefile=sys.argv[1]
	image=imread(imagefile,as_grey=True)
	image_featurization(image)

if __name__=="__main__":
	main()
	

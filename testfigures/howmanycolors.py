from PIL import Image
import colorsys
import pickle

def HSVColor(img):
	if isinstance(img,Image.Image):
		r,g,b = img.split()
		Hdat = []
		Sdat = []
		Vdat = [] 
		for rd,gn,bl in zip(r.getdata(),g.getdata(),b.getdata()) :
			h,s,v = colorsys.rgb_to_hsv(rd/255.,gn/255.,bl/255.)
			Hdat.append(int(h*255.))
			Sdat.append(int(s*255.))
			Vdat.append(int(v*255.))
		r.putdata(Hdat)
		g.putdata(Sdat)
		b.putdata(Vdat)
		return Image.merge('RGB',(r,g,b))
	else:
		return None

def main():
	im=Image.open("remapcolortable.png").convert('RGB')
	hsvim=HSVColor(im)
	print len(im.getcolors())
	pickle.dump(hsvim,open('hsvremap.Im.pickle',"w"))
	hsvim.show()

if __name__=="__main__":
	main()

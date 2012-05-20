#!/usr/bin/python2

import Image
import glob, os, re
from math import sqrt


class PhotoPix:
	def __init__(self, filename, color):
		self.filename = filename
		self.color = color

class Photo:
	def __init__(self, basefile):
		#assert width*2 == height*3
		self.basefile = basefile
		im = Image.open(self.basefile)
		im = im.convert('RGB')
		(basewidth, baseheight) = im.size
		self.width = basewidth
		self.height = baseheight
		self.baseim = im
		self.pix = im.load()
	def save(self, filename):
		self.baseim.save(filename)

from colormath.color_objects import RGBColor

def ColorDistance(pix1, pix2):
	'''Computes euclidian distance beween two colors.
	if improvement needed : http://en.wikipedia.org/wiki/Color_difference'''
	#dist = sqrt ( pow(pix1[0]-pix2[0],2)+pow(pix1[1]-pix2[1],2)+pow(pix1[2]-pix2[2],2) )
	col1 = RGBColor(pix1[0], pix1[1], pix1[2])
	col2 = RGBColor(pix2[0], pix2[1], pix2[2])
	#dist = col1.delta_e(col2, mode='cmc', pl=1, pc=1)
	dist = col1.delta_e(col2)
	return dist

Available = []

for infile in glob.glob("Photos/*.1px.png"):
	im = Image.open(infile)
	im = im.convert('RGB')
	data = list(im.getdata())
	print (infile + ": " + str(data[0]))
	photofile = re.sub('1px.png', 'min.jpg', infile)
	Available.append( PhotoPix(photofile, data[0] ))

ph = Photo("Base/base.png")
filelist = []

log = open("mosaique.log", "w")
for rowi in range (ph.height):
	print ("Processing row "+str(rowi))
	for coli in range (ph.width):
		pix = ph.pix[coli,rowi]
		distance = 10000
		for image in Available:
			tempdist = ColorDistance(pix, image.color)
			if tempdist < distance:
				distance=tempdist
				choosen = image
		log.write ("Line "+str(rowi)+" Col "+str(coli)+": "+choosen.filename+" (distance: "+str(distance)+")\n")
		ph.pix[coli,rowi]=choosen.color
		filelist.append(choosen.filename)

ph.save("result.pix.png")

out = open("montage.sh", "w")
out.write("montage -tile "+str(ph.width)+"x"+str(ph.height)+" -geometry +0+0 \\\n")
for filename in filelist:
	out.write(filename + " \\\n")
out.write("test.jpg")
out.close()
	

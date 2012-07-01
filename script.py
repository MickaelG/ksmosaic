#!/usr/bin/python2
# -*- coding: utf-8 -*-

import Image
import glob, os, re, stat
import random
from math import sqrt


class PhotoMin:
	def __init__(self, filename, color):
		self.filename = filename
		self.color = color
		self.used = 0

class Pixel:
	def __init__(self, photo, target_color, distance, min_distance):
		self.photo = photo
		self.distance = distance
		self.min_distance = min_distance
		self.target_color = target_color
		self.used = 0

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
		self.array = {}
	
	def read_available_miniatures(self):
		self.available_min = []
		for infile in glob.glob("work/*.1px.png"):
			im = Image.open(infile)
			im = im.convert('RGB')
			data = list(im.getdata())
			print (infile + ": " + str(data[0]))
			photofile = re.sub('1px.png', 'min.jpg', infile)
			self.available_min.append( PhotoMin(photofile, data[0] ))

	def fill(self, rand=True):
		rand_filelist = []
		dist_threshold = 12
		for rowi in range (self.height):
			print ("Processing row "+str(rowi))
			for coli in range (self.width):
				pix = self.pix[coli,rowi]
				min_distance = 10000
				distlist = []
				for image in self.available_min:
					tempdist = ColorDistance(pix, image.color)
					#print ("Distance: " + image.filename + " " + str(tempdist))
					if tempdist < min_distance:
						min_distance=tempdist
						choosen = image
						#print ("Choosen as min dist")
					if tempdist < dist_threshold:
						#print ("Added to random list")
						distlist.append( (tempdist,image) )
				if rand:
					chooselist = []
					for elem in distlist:
						nb_elem = int(10*(dist_threshold-elem[0]))
						for i in range(nb_elem):
							chooselist.append(elem)
					if len(chooselist) > 0:
						rand_choosen = chooselist[random.randrange(len(chooselist))]
					else:
						rand_choosen = (min_distance,choosen)
				else:
					rand_choosen = (min_distance,choosen)
				#print ("Choosen : " + rand_choosen.filename)
				self.pix[coli,rowi]=rand_choosen[1].color
				self.array[coli,rowi]=Pixel(rand_choosen[1], pix, rand_choosen[0], min_distance)
				rand_choosen[1].used += 1

	def add_missing(self):
		NotUsed = []
		for image in self.available_min:
			if image.used == 0:
				NotUsed.append(image)
		for image in NotUsed:
			min_distance = 10000
			for rowi in range (self.height):
				for coli in range (self.width):
					if self.array[coli,rowi].photo.used > 1:
						pix = self.pix[coli,rowi]
						tempdist = ColorDistance(pix, image.color)
						if tempdist < min_distance:
							min_distance=tempdist
							choosen = (coli,rowi)
			self.pix[choosen]=image.color
			self.array[choosen].photo.used -= 1
			self.array[choosen].photo = image
			self.array[choosen].photo.used += 1
			self.array[choosen].distance = min_distance
			print ( "Missing " + image.filename + " set at (" + str(choosen) + ")" )

	def report_min_usage(self, filename):
		out = open(filename, "w")
		for image in self.available_min:
			out.write(image.filename + " utilisé " + str(image.used) + " fois\n")
		out.close()
	def report_distance(self,filename):
		data={}
		for rowi in range (self.height):
			for coli in range (self.width):
				pix = self.array[coli,rowi]
				data[pix.distance] = "Line "+str(rowi)+" Col "+str(coli)+": "+pix.photo.filename+" (distance: "+str(pix.distance)+", min_distance"+str(pix.min_distance)+")"
		log = open(filename, "w")
		for key in sorted(data.iterkeys()):
			log.write (data[key]+"\n")
		log.close()

	def write_im_script(self, im_script_file, log_file):
		log = open(log_file, "w")
		out = open(im_script_file, "w")
		out.write("#!/bin/sh\n\n")
		out.write("montage -tile "+str(self.width)+"x"+str(self.height)+" -geometry +0+0 \\\n")
		for rowi in range (self.height):
			for coli in range (self.width):
				pix = self.array[coli,rowi]
				out.write(pix.photo.filename + " \\\n")
				log.write ("Line "+str(rowi)+" Col "+str(coli)+": "+pix.photo.filename+" (distance: "+str(pix.distance)+", min_distance"+str(pix.min_distance)+")\n")
		out.write("test.jpg")
		out.close()

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


ph = Photo("base.png")
ph.read_available_miniatures()

ph.fill(rand=True)
#ph.fill(rand=False)
ph.save("beffill_result.pix.png")
ph.write_im_script("beffill_montage.sh", "beffill_mosaique.log")
ph.report_min_usage("beffill_photos.used.log")

ph.add_missing()
ph.save("result.pix.png")
ph.write_im_script("montage.sh", "mosaique.log")
ph.report_min_usage("photos.used.log")
ph.report_distance("distance.log")


#!/usr/bin/python2
# -*- coding: utf-8 -*-

import sys
import ksmosaic.image_pil as imagelib
#import ksmosaic.image_wand as imagelib
import ksmosaic.color as color

import glob, os, errno
import random

#import pdb
#pdb.set_trace()

def read_conf(configfile):
	import ConfigParser
	config=ConfigParser.ConfigParser()
	config.read(configfile)
	conf = {}
	param_list = [ "MOSAIC_IMAGE", "OUT_FILE_NAME", "MOSAIC_SIZE",
	               "IMAGES_DIR", "IMAGES_SIZE",
	               "MIN_USAGE", "MAX_USAGE", "WORK_DIR", "SURIMP_PERCENT" ]
	for param in param_list:
		conf[param] = config.get("parameters", param)
	conf['IMAGES_SIZE'] = [int(elem) for elem in conf['IMAGES_SIZE'].split("x")]
	conf['MOSAIC_SIZE'] = [int(elem) for elem in conf['MOSAIC_SIZE'].split("x")]
	conf['MAX_USAGE'] = int(conf['MAX_USAGE'])
	conf['MIN_USAGE'] = int(conf['MIN_USAGE'])
	conf['SURIMP_PERCENT'] = int(conf['SURIMP_PERCENT'])
	return conf

class Photo:
	def __init__(self, filename, color, min_occurences=None, max_occurences=None):
		self.filename = os.path.basename(filename)
		self.color = color
		self.used = 0
		self.min_occurences = min_occurences
		self.max_occurences = max_occurences

class PhotoList(list):
	def __init__(self, input_dir=None):
		list.__init__(self)
		if input_dir:
			self.read_available(input_dir)
	def read_available(self, input_dir):
		glob_1px = input_dir + "/*"
		for infile in glob.glob(glob_1px):
			(width, height, data) = imagelib.read(infile)
			if width != 1 or height != 1:
				raise StdError("%s should be a 1px image" % (infile))
			print (infile + ": " + str(data[0,0]))
			self.append( Photo(infile, data[0,0] ))
	def write_images_color(self, filename):
		outf = open(filename, "w")
		for image in self:
			outf.write("%s	%s\n" % (image.filename, image.color))
	def report_min_usage(self, filename):
		out = open(filename, "w")
		for min_image in self:
			out.write(min_image.filename + " utilisé " + str(min_image.used) + " fois\n")
		out.close()

class Pixel:
	def __init__(self, target_color, photo=None, distance=None):
		self.target_color = target_color
		self.photo = None
		self.distance = None
		self.min_distance = None
		if self.photo:
			self.set_photo(photo, distance)
	def set_photo(self, photo, distance):
		if self.photo:
			self.photo.used -= 1
		self.photo = photo
		self.photo.used += 1
		if self.min_distance == None or self.min_distance > distance:
			self.min_distance = distance
		self.distance = distance

class Mosaic:
	def __init__(self, image):
		self.image = image
		(self.width, self.height, pix_array) = imagelib.read(self.image)
		self.array = {}
		for x in range(self.width):
			for y in range(self.height):
				self.array[x,y] = Pixel(pix_array[x,y])

	def fill(self, photo_list, max_photo_usage=20):
		rand_filelist = []
		dist_threshold = 12
		print ("Starting fill…")
		colrowList = []
		for rowi in range (self.height):
			for coli in range (self.width):
				colrowList.append( (coli, rowi) )
		random.shuffle(colrowList)
		# We fill pixels in random order so we can easily limit
		# the number of usages of a photo
		for index, (coli, rowi) in enumerate(colrowList):
			if index % self.width == 0:
				print ("%i/%i points processed (%i%%)" % (index, self.width*self.height, index/(self.width*self.height)))
			pix = self.array[coli,rowi]
			min_distance = 10000
			around_list = []
			for c in (coli-1, coli, coli+1):
				for r in (rowi-1, rowi, rowi+1):
					try:
						around_list.append( self.array[c,r].photo )
					except KeyError:
						None
			choosen = None
			for min_image in photo_list:
				if min_image.used < max_photo_usage and min_image not in around_list:
					tempdist = color.get_distance(pix.target_color, min_image.color)
					if tempdist < min_distance:
						min_distance=tempdist
						choosen = min_image
			self.array[coli,rowi].set_photo(choosen, min_distance)

	def add_missing(self, photo_list, min_photo_usage=1):
		"""
		Add some photos in the mosaic to respect the min usage parameter
		"""
		to_be_corrected = []
		for min_image in photo_list:
			if min_image.used < min_photo_usage:
				to_be_corrected.append(min_image)
		for min_image in to_be_corrected:
			for nb in range(min_photo_usage-min_image.used):
				min_distance = 10000
				for rowi in range (self.height):
					for coli in range (self.width):
						if self.array[coli,rowi].photo.used > min_photo_usage:
							pix = self.array[coli,rowi]
							tempdist = color.get_distance(pix.target_color, min_image.color)
							if tempdist < min_distance:
								min_distance=tempdist
								choosen_location = (coli,rowi)
				self.array[choosen_location].set_photo(min_image, min_distance)
				print ( "Missing " + min_image.filename + " set at (" + str(choosen_location) + ")" )

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

	def list_generator(self, directory):
		for rowi in range (self.height):
			for coli in range (self.width):
				pix = self.array[coli,rowi]
				yield directory+pix.photo.filename

def create_min_images( input_dir, output_dir, size, force=False ):
	"""
	For each file in input_dir, reates a resized version of an image
	with the given size
	If the out image exists and is more recent that the one in input,
	the resize is not run if force is not True.
	"""
	for infile in glob.glob(input_dir+"/*"):
		filename = os.path.basename(infile)
		outfile = output_dir + "/" + filename
		if force or (not os.path.exists(outfile)) or os.path.getmtime(infile) > os.path.getmtime(outfile):
			imagelib.resize( infile, outfile, size )

def mkdir(dirname):
	try:
		os.mkdir(dirname)
	except OSError as exc: # Python >2.5
		if exc.errno == errno.EEXIST and os.path.isdir(dirname):
			pass
		else:
			raise

def main():
	conf = read_conf(sys.argv[1])

	work_dir = conf['WORK_DIR']+"/"
	min_images_dir = work_dir+"min_"+"x".join([str(elem) for elem in conf['IMAGES_SIZE']])+"/"
	px_images_dir = work_dir+"1px/"
	mkdir(work_dir)
	mkdir(min_images_dir)
	mkdir(px_images_dir)
	mosaic_size = conf['MOSAIC_SIZE']
	image_size = conf['IMAGES_SIZE']

	create_min_images( conf['IMAGES_DIR'], min_images_dir, image_size )
	#we build 1px images from miniatures to save computing time
	create_min_images( min_images_dir, px_images_dir, (1,1) )

	imagelib.resize( conf['MOSAIC_IMAGE'], work_dir+"/pix.jpg", mosaic_size )
	ph = Mosaic(work_dir+"/pix.jpg")
	photo_list = PhotoList(px_images_dir)

	ph.fill(photo_list, max_photo_usage=conf['MAX_USAGE'])
	ph.add_missing(photo_list, min_photo_usage=conf['MIN_USAGE'])
	ph.write_im_script(work_dir+"montage.sh", work_dir+"mosaique.log")
	photo_list.report_min_usage(work_dir+"photos.used.log")
	ph.report_distance(work_dir+"distance.log")

	imagelib.montage ( ph.width, ph.height, list(ph.list_generator(min_images_dir)), work_dir+"out.jpg" )

	total_size = (mosaic_size[0]*image_size[0], mosaic_size[1]*image_size[1])
	resized_image_file = work_dir+"/resized.jpg"
	imagelib.resize( conf['MOSAIC_IMAGE'], resized_image_file, total_size )
	imagelib.blend( resized_image_file, work_dir+"out.jpg", conf['OUT_FILE_NAME'], conf['SURIMP_PERCENT'] )

if __name__ == "__main__":
	main()


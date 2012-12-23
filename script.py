#!/usr/bin/python2
# -*- coding: utf-8 -*-

import sys
import ksmosaic.image_pil as imagelib
#import ksmosaic.image_wand as imagelib
import ksmosaic.color as color
import ksmosaic.configuration as config

import glob, os, errno
import random

#import pdb
#pdb.set_trace()


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
	def sort_by_brightness(self):
		self.sort(key=lambda elem: color.get_brightness(elem.color))
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
	def __init__(self, target_color=None, photo=None, distance=None):
		self.target_color = target_color
		self.photo = None
		self.distance = None
		self.min_distance = None
		if self.photo:
			self.set_photo(photo, distance)
	def set_photo(self, photo, distance=None):
		if self.photo:
			self.photo.used -= 1
		self.photo = photo
		self.photo.used += 1
		if self.min_distance == None or self.min_distance > distance:
			self.min_distance = distance
		self.distance = distance

class Mosaic:
	def __init__(self, image=None, size=None):
		self.array = {}
		self.image = image
		if image:
			(self.width, self.height, pix_array) = imagelib.read(self.image)
			for pix in self.iter_pix():
				self.array[pix] = Pixel(pix_array[pix])
		else:
			self.width = size[0]
			self.height = size[1]
			for pix in self.iter_pix():
				self.array[pix] = Pixel()

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

	def get_border_length(self, offset=0):
		return 2*self.width + 2*self.height - 4 - 8*offset
	def add_border(self, photo_list, offset=0):
		for index, pix in enumerate(self.iter_border(offset)):
			photo_index = index % len(photo_list)
			self.array[pix].set_photo(photo_list[photo_index])

	def iter_pix(self):
		for x in range(self.width):
			for y in range(self.height):
				yield(x,y)

	def iter_border(self, offset=0):
		for x in range(offset, self.width-offset):
			yield(x,offset)
		for y in range(offset+1, self.height-offset-1):
			yield(self.width-1-offset, y)
		for x in reversed(range(offset, self.width-offset)):
			yield(x,self.height-1-offset)
		for y in reversed(range(offset+1, self.height-offset-1)):
			yield(offset,y)

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
				if pix.photo:
					yield directory+pix.photo.filename
				else:
					yield None

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
	main_mosaic()
	#main_test()

def main_mosaic():
	conf = config.Conf(sys.argv[1])

	setup_work_dir ( conf.images_dir, conf.work_dir, conf.min_images_dir, conf.images_size, conf.px_images_dir )

	ph = Mosaic(image=conf.work_dir+"/pix.jpg")
	photo_list = PhotoList(conf.px_images_dir)

	ph.fill(photo_list, max_photo_usage=conf.max_usage)
	ph.add_missing(photo_list, min_photo_usage=conf.min_usage)
	ph.write_im_script(conf.work_dir+"montage.sh", conf.work_dir+"mosaique.log")
	photo_list.report_min_usage(conf.work_dir+"photos.used.log")
	ph.report_distance(conf.work_dir+"distance.log")

	imagelib.montage ( (ph.width, ph.height), conf.images_size, list(ph.list_generator(conf.min_images_dir)), conf.work_dir+"out.jpg" )

	resized_image_file = conf.work_dir+"/resized.jpg"
	imagelib.resize( conf.mosaic_image, resized_image_file, conf.total_size )
	imagelib.blend( resized_image_file, conf.work_dir+"out.jpg", conf.out_file_name, conf.surimp )

def setup_work_dir ( images_dir, work_dir, min_images_dir, min_images_size, px_images_dir ):
	mkdir(work_dir)
	mkdir(min_images_dir)
	mkdir(px_images_dir)
	create_min_images( images_dir, min_images_dir, min_images_size )
	#we build 1px images from miniatures to save computing time
	create_min_images( images_dir, px_images_dir, (1,1) )

def main_test():
	conf = config.Conf(sys.argv[1])

	setup_work_dir ( conf.images_dir, conf.work_dir, conf.min_images_dir, conf.images_size, conf.px_images_dir )

	ph = Mosaic(size=conf.mosaic_size)
	photo_list = PhotoList(conf.px_images_dir)

	photo_list.sort_by_brightness()
	nb_light_photos = ph.get_border_length(0) + ph.get_border_length(1) + ph.get_border_length(2) + ph.get_border_length(3)
	nb_dark_photos = ph.get_border_length(4)

	dark_photo_list = photo_list[0:nb_dark_photos]
	light_photo_list = photo_list[len(photo_list)-nb_light_photos:]

	random.shuffle(dark_photo_list)
	random.shuffle(light_photo_list)

	ph.add_border ( light_photo_list, 0 )
	del(light_photo_list[0:ph.get_border_length(0)])
	ph.add_border ( light_photo_list, 1 )
	del(light_photo_list[0:ph.get_border_length(1)])
	ph.add_border ( light_photo_list, 2 )
	del(light_photo_list[0:ph.get_border_length(2)])
	ph.add_border ( light_photo_list, 3 )

	ph.add_border ( dark_photo_list, 4 )

	photo_list.report_min_usage(conf.work_dir+"photos.used.log")

	imagelib.montage ( (ph.width, ph.height), conf.images_size,
	                   list(ph.list_generator(conf.min_images_dir)),
	                   conf.work_dir+"out.jpg" )

if __name__ == "__main__":
	main()



from wand.image import Image

def resize( input_file, output_file, size ):
	"""
	convert -resize $(size) input_file output_file_or_dir
	"""
	if __debug__:
		print ("Resizing image: %s (size:%ix%i)" % (input_file, size[0], size[1]))
	with Image(filename=input_file) as im:
		im.resize(size[0], size[1])
		im.save(filename=output_file)


def blend( input_file1, input_file2, output_file, surimp_percent ):
	"""
	composite -blend $(SURIMP_PERCENT) base.jpg input output
	"""
	with Image(filename=input_file2) as background, \
	     Image(filename=input_file1) as im:
		background.watermark(im, 1-(surimp_percent/100.0))
		background.save(filename=output_file)


def montage ( width, height, input_list, output_file ):
	"""
	montage -tile "width"x"height" -geometry +0+0 input_list output_file
	"""
	(img_width, img_height, pix) = read(input_list[0], get_pix=False)
	total_width = width*img_width
	total_height = height*img_height
	with Image(width=total_width, height=total_height) as res_image:
		for x in range(width):
			for y in range(height):
				with Image(filename=input_list[x+width*y]) as im:
					res_image.composite(im, x*img_width, y*img_height)
		res_image.save(filename=output_file)


def read( input_file, get_pix=True ):
	"""
	Takes the input file name as argument
	returns a 3-tuple :
	- width
	- height
	- pix : dictionary of pixels in RGB, addressed by (x,y) tuple
	"""
	if __debug__:
		print("Reading image file: %s" % (input_file))
	with Image(filename=input_file) as im:
		pix = {}
		width = im.width
		height = im.height
		if get_pix:
			for x in range(im.width):
				for y in range(im.height):
					color = im[x,y]
					pix[x,y] = ( color.red/256, color.green/256, color.blue/256 )
	return ( width, height, pix )


import Image

def resize( input_file, output_file, size ):
	"""
	convert -resize $(size) input_file output_file_or_dir
	"""
	#TODO

def composite( input_file, output_file, surimp_percent ):
	"""
	composite -blend $(SURIMP_PERCENT) base.jpg input output
	"""
	#TODO

def montage ( width, height, input_list, output_file )
	"""
	montage -tile "width"x"height" -geometry +0+0 input_list output_file
	"""
	#TODO

def read( input_file ):
	"""
	Takes the input file name as argument
	returns a 3-tuple :
	- width
	- height
	- pix : dictionary of pixels in RGB, addressed by (x,y) tuple
	"""
	im = Image.open(input_file)
	im = im.convert('RGB')
	(basewidth, baseheight) = im.size
	pix = im.load()

	return ( width, height, pix )


import Image

def resize( input_file, output_file, size ):
	"""
	convert -resize $(size) input_file output_file_or_dir
	"""
	if __debug__:
		print ("Resizing image: %s (size:%ix%i)" % (input_file, size[0], size[1]))
	im = Image.open(input_file)
	result = im.resize(size, Image.ANTIALIAS)
	result.save(output_file)


def blend( input_file1, input_file2, output_file, surimp ):
	"""
	composite -blend $(SURIMP_PERCENT) base.jpg input output
	"""
	background = Image.open(input_file1)
	im = Image.open(input_file2)
	result = Image.blend(im, background, surimp)
	result.save(output_file)


def montage ( size, img_size, input_list, output_file ):
	"""
	montage -tile "width"x"height" -geometry +0+0 input_list output_file
	"""
	(width, height) = size
	(img_width, img_height) = img_size
	total_width = width*img_width
	total_height = height*img_height
	res_image = Image.new('RGB', (total_width, total_height), None)
	for x in range(width):
		for y in range(height):
			image = input_list[x+width*y]
			if image:
				im = Image.open(image)
				res_image.paste( im, (x*img_width, y*img_height))
	res_image.save(output_file)


def read( input_file ):
	"""
	Takes the input file name as argument
	returns a 3-tuple :
	- width
	- height
	- pix : dictionary of pixels in RGB, addressed by (x,y) tuple
	"""
	if __debug__:
		print("Reading image file: %s" % (input_file))
	im = Image.open(input_file)
	im = im.convert('RGB')
	(width, height) = im.size
	pix = im.load()

	return ( width, height, pix )

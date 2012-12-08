
try:
	from colormath.color_objects import RGBColor
	HasColormath=True
except ImportError:
	print "WARNING: colormath module not available. will use euclidian RGB distance to replace it"
	HasColormath=False
	from math import sqrt


def get_distance(pix1, pix2):
	'''Computes distance beween two colors. based on colormath if available,
	   or computes a simple euclidian distance on RGB values
	'''
	if HasColormath:
		col1 = RGBColor(pix1[0], pix1[1], pix1[2])
		col2 = RGBColor(pix2[0], pix2[1], pix2[2])
		#dist = col1.delta_e(col2, mode='cmc', pl=1, pc=1)
		dist = col1.delta_e(col2)
	else:
		dist = sqrt ( pow(pix1[0]-pix2[0],2)+pow(pix1[1]-pix2[1],2)+pow(pix1[2]-pix2[2],2) )
	return dist

def get_brightness(rgb_color):
	return (0.299*rgb_color[0] + 0.587*rgb_color[1] + 0.114*rgb_color[2])

def get_saturation(rgb_color):
	import colorsys
	(h,l,s) = colorsys.rgb_to_hls( *rgb_color )
	return s


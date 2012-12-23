
class Conf():
	def __init__(self, configfile):
		import ConfigParser
		config=ConfigParser.ConfigParser()
		config.read(configfile)
		conf = {}
		param_list = [ "MOSAIC_IMAGE", "OUT_FILE_NAME", "MOSAIC_SIZE",
		               "IMAGES_DIR", "IMAGES_SIZE",
		               "MIN_USAGE", "MAX_USAGE", "WORK_DIR", "SURIMP_PERCENT" ]
		for param in param_list:
			conf[param] = config.get("parameters", param)

		self.images_size = [int(elem) for elem in conf['IMAGES_SIZE'].split("x")]
		self.mosaic_size = [int(elem) for elem in conf['MOSAIC_SIZE'].split("x")]
		self.max_usage = int(conf['MAX_USAGE'])
		self.min_usage = int(conf['MIN_USAGE'])
		self.surimp = int(conf['SURIMP_PERCENT'])/100.0
		self.work_dir = conf['WORK_DIR']+"/"
		self.images_dir = conf['IMAGES_DIR']
		self.mosaic_image = conf['MOSAIC_IMAGE']
		self.out_file_name = conf['OUT_FILE_NAME']
		self.min_images_dir = self.work_dir+"min_"+"x".join([str(elem) for elem in self.images_size])+"/"
		self.px_images_dir = self.work_dir+"1px/"
		self.total_size = (self.mosaic_size[0]*self.images_size[0], self.mosaic_size[1]*self.images_size[1])



include Makefile.conf

default: test_surimp.jpg

test.jpg: montage.sh
	./montage.sh

montage.sh: base.png script.py
	cd Photos && make MIN_SIZE=$(MIN_SIZE)
	./script.py
	chmod 775 montage.sh

test_surimp.jpg: test.jpg base.jpg
	composite -blend $(SURIMP_PERCENT) base.jpg $< $@

base.png: $(IN_FILE) Makefile.conf
	convert -resize $(MOS_SIZE) $< $@

base.jpg: $(IN_FILE) Makefile.conf
	convert -resize $(MOS_SIZE_PIX) $< $@

cleanRes:
	rm -f *.pix.png
	rm -f test*.jpg
	rm -f *.log
	rm -f *montage.sh
	cd Photos && make cleanRes


include Makefile.conf

default: test_surimp.jpg

test.jpg: montage.sh all_min
	./montage.sh

montage.sh: base.png script.py all_1px
	./script.py
	chmod 775 montage.sh

test_surimp.jpg: test.jpg base.jpg
	composite -blend $(SURIMP_PERCENT) base.jpg $< $@

base.png: $(IN_FILE) Makefile.conf
	convert -resize $(MOS_SIZE) $< $@

base.jpg: $(IN_FILE) Makefile.conf
	convert -resize $(MOS_SIZE_PIX) $< $@

save: DIR=result_$(shell date +%Y%m%d_%Hh%M)
save:
	mkdir $(DIR)
	cp test*.jpg $(DIR)
	cp *.log $(DIR)
	cp *montage.sh $(DIR)
	cp $(IN_FILE) $(DIR)
	cp result.pix.png $(DIR)
	cp Makefile.conf $(DIR)

clean:
	rm -f $(WORK_DIR)/*.1px.png
	rm -f $(WORK_DIR)/*.min.jpg

cleanRes: clean
	rm -f *.pix.png
	rm -f test*.jpg
	rm -f *.log
	rm -f *montage.sh
	cd Photos && make cleanRes


## Min photos build
ALL_PHOTOS_M = $(wildcard $(PHOTOS_DIR)/*.JPG)
ALL_PHOTOS_M_DIR = $(subst $(PHOTOS_DIR),$(WORK_DIR),$(ALL_PHOTOS_M))
ALL_1PX_TARGETS = $(subst JPG,1px.png,$(ALL_PHOTOS_M_DIR))
ALL_MIN_TARGETS = $(subst JPG,min.jpg,$(ALL_PHOTOS_M_DIR))

all_min: $(ALL_MIN_TARGETS)
all_1px: $(ALL_1PX_TARGETS)

$(WORK_DIR)/%.1px.png: $(PHOTOS_DIR)/%.JPG
	convert -resize '1x1!' $< $@

$(WORK_DIR)/%.min.jpg: $(PHOTOS_DIR)/%.JPG
	convert -resize $(MIN_SIZE) $< $@

ALL_1PX_BW_TARGETS = $(subst 1px,1px_bw,$(ALL_1PX_TARGETS))
all_bw: $(ALL_1PX_BW_TARGETS)

$(WORK_DIR)/%.1px_bw.png: $(WORK_DIR)/%.min_bw.jpg
	convert -resize '1x1!' $< $@

$(WORK_DIR)/%.min_bw.jpg: $(PHOTOS_DIR)/%.JPG
	convert -colorspace Gray -resize $(MIN_SIZE) $< $@

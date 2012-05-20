
ALL_PHOTOS = $(wildcard *.JPG)
ALL_1PX_TARGETS = $(subst JPG,1px.png,$(ALL_PHOTOS))
ALL_MIN_TARGETS = $(subst JPG,min.jpg,$(ALL_PHOTOS))

all: $(ALL_1PX_TARGETS) $(ALL_MIN_TARGETS)

%.1px.png: %.JPG
	convert -resize '1x1!' $< $@

MIN_SIZE=150x100
MIN_SIZE=15x10
%.min.jpg: %.JPG Makefile
	convert -resize $(MIN_SIZE) $< $@

clean:
	rm -f *.1px.png
	rm -f *.min.jpg


all:
	cd Photos && make
	cd Base && make
	./script.py
	. montage.sh

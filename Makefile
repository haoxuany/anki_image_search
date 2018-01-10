ZIPNAME = addon.zip

clean:
	rm -rf *.pyc __pycache__/ $(ZIPNAME)

pack:
	make clean
	zip -r $(ZIPNAME) *

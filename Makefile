#

PYTHON=`which python`

all:
	@echo "make source - Create source package"
	@echo "make install - Install on local system"
	@echo "make clean - Get rid of scratch and byte files"

source:
	$(PYTHON) setup.py sdist 

install:
	$(PYTHON) setup.py install 

clean:
	$(PYTHON) setup.py clean
	rm -rf build/ dist/ nubo.egg-info/ MANIFEST 
	find . -name '*.pyc' -delete
    

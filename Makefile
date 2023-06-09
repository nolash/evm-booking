all: solidity python

solidity:
	make -C solidity install

doc:
	make -C doc/texinfo

readme:
	make -C doc/texinfo readme
	pandoc -f docbook -t gfm doc/texinfo/build/docbook.xml > README.md

python:
	make -C python

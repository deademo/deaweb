dist:
	python setup.py sdist --formats=gztar
	-cd dist && del *.orig

clean:
	-rmdir /s /q dist

upload:
	pip install twine
	twine upload dist/*

all: clean dist upload
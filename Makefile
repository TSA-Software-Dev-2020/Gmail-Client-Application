.PHONY: virtualenv

setup:
	if [ ! -d env ]
	then
		. $virtualenv env
	fi
	env/Scripts/activate
	pip install -r requirements.txt
	

run:
	. env/Scripts/activate
	python main.py
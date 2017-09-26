.DEFAULT: null
.PHONY: null
null:
	@echo No Default Target
	
venv:
	python -mvenv venv
	
	
.PHONY: lint
lint:
	autopep8 -aaaaaa -i -r opensda_flasher
	isort
	flake8
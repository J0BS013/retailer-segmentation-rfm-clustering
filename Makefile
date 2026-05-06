.PHONY: run notebook test install

install:
	pip install -r requirements.txt

run:
	python src/run_pipeline.py

notebook:
	jupyter lab --ip=0.0.0.0 --port=8888 --no-browser

test:
	python -m pytest tests/ -v

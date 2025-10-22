install:
	python -m pip install -r requirements.txt

dev-install:
	python -m pip install -r requirements.txt
	python -m pip install ruff pytest

format:
	python -m ruff format .

lint:
	python -m ruff check --select I,RUF022 --fix .

check:
	python -m ruff check .

mark-video-zone:
	@echo "Usage: make mark-video-zone VIDEO=path/to/video.mp4"
	@echo "Example: make mark-video-zone VIDEO=data/853874-hd_1920_1080_25fps.mp4"
	@if [ -z "$(VIDEO)" ]; then \
		echo "Error: VIDEO parameter is required"; \
		exit 1; \
	fi
	python scripts/zone_creation.py $(VIDEO)

run:
	python run.py

run-ui:
	python run_ui.py

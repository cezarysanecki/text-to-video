VENV := .venv
PYTHON := $(VENV)/bin/python
PYCAPS := $(VENV)/bin/pycaps

# Workflow parameters (override on the command line, e.g. `make subs VIDEO=clip.mp4`)
VIDEO ?= test.mp4
TEMPLATE ?= minimalist
SUBS ?= $(basename $(VIDEO)).subs.json
OUTPUT ?= $(basename $(VIDEO)).captioned.mp4

.PHONY: setup venv install browser check clean templates subs subs-edit edit render render-reflow preview

## Full setup: venv + dependencies + Playwright browser
setup: venv install browser check

venv:
	uv venv --python 3.12 $(VENV)

install:
	uv pip install -e ".[base]" "numba==0.60.0" "llvmlite==0.43.0" --python $(PYTHON)
	uv pip install "numpy<2" --python $(PYTHON)

browser:
	$(VENV)/bin/playwright install chromium

## Verify the installation works
check:
	$(PYCAPS) --help > /dev/null
	$(PYTHON) -c "import whisper, torch, numpy; print('OK: torch', torch.__version__, '| numpy', numpy.__version__)"

## List available templates
templates:
	$(PYCAPS) template list

## Step 1: transcribe only -> writes $(SUBS) for manual correction (no video render)
subs:
	$(PYTHON) scripts/generate_subs.py $(VIDEO) --template $(TEMPLATE)

## Step 1 (GUI): transcribe, open the graphical editor, save corrected $(SUBS)
subs-edit:
	$(PYTHON) scripts/generate_subs.py $(VIDEO) --template $(TEMPLATE) --edit

## Edit an existing subtitle data JSON in the GUI editor (no transcription)
edit:
	$(PYTHON) scripts/edit_subs.py $(SUBS)

## Step 2: render the video using the (corrected) subtitle data JSON
render:
	rm -f $(OUTPUT)
	$(PYCAPS) render --input $(VIDEO) --template $(TEMPLATE) --subtitle-data $(SUBS) --output $(OUTPUT)

## Step 2 (reflow): render keeping texts/timings from $(SUBS) but recalculating
## line breaks for the current template — use after switching to a template
## with a different font size
render-reflow:
	rm -f $(OUTPUT)
	$(PYCAPS) render --input $(VIDEO) --template $(TEMPLATE) --transcript $(SUBS) --transcript-format pycaps_json --output $(OUTPUT)

## Quick low-quality preview render (full pipeline, incl. transcription)
preview:
	$(PYCAPS) render --input $(VIDEO) --template $(TEMPLATE) --preview

## Remove the virtual environment
clean:
	rm -rf $(VENV)

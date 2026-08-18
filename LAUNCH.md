# Running pycaps locally

How to set up and run this repository on this machine (macOS, Intel x86_64).

## Requirements

- **FFmpeg** — must be on `PATH` (installed: `/usr/local/bin/ffmpeg`)
- **Python 3.10–3.12** — the project does NOT work on 3.13/3.14 (system Python is 3.14, hence the 3.12 venv)
- **uv** — for managing the venv (optional; plain `python -m venv` + `pip` works too)

There is no `requirements.txt` — all dependencies are defined in `pyproject.toml`.

## Setup

Quickest way — use the Makefile:

```bash
make setup
```

Or manually:

```bash
# 1. Create a venv with Python 3.12
uv venv --python 3.12 .venv

# 2. Install the project (editable) with Intel Mac pins
uv pip install -e ".[base]" "numba==0.60.0" "llvmlite==0.43.0" --python .venv/bin/python
uv pip install "numpy<2" --python .venv/bin/python

# 3. Browser for Playwright (CSS subtitle rendering)
.venv/bin/playwright install chromium
```

### Why these pins? (Intel Mac specifics)

| Pin | Reason |
|---|---|
| `numba==0.60.0`, `llvmlite==0.43.0` | Newer versions ship no prebuilt wheels for macOS x86_64 — they try to build from source (needs cmake + LLVM) and the install fails |
| `numpy<2` (1.26.4) | `torch` 2.2.2 is the last version supporting Intel Macs and is built against numpy 1.x — imports break with numpy 2.x |

On Apple Silicon or Linux these pins are unnecessary — plain `pip install -e ".[base]"` is enough.

## Usage

```bash
# Activate the environment
source .venv/bin/activate

# List available templates
pycaps template list

# Render a video with subtitles (Whisper transcription)
pycaps render --input my_video.mp4 --template minimalist

# If you already have a transcript (whisper_json / pycaps_json / srt / vtt):
pycaps render --input my_video.mp4 --template minimalist --transcript transcript.json

# Preview template styles without rendering
pycaps preview-styles --template minimalist
```

Without activating the venv: `.venv/bin/pycaps render ...`

### Two-step workflow: correct the transcript before rendering

```bash
# Step 1: transcribe only — writes test.subs.json, no video render
make subs VIDEO=test.mp4

# Step 1 alternative: transcribe + open the GUI editor (friendlier than raw JSON);
# the corrected result is saved to test.subs.json
make subs-edit VIDEO=test.mp4

# Edit an existing subs JSON in the GUI editor anytime (no re-transcription):
make edit SUBS=test.subs.json

# Step 2: edit test.subs.json by hand (fix typos, timings), then render:
make render VIDEO=test.mp4                      # uses test.subs.json by default
make render VIDEO=test.mp4 TEMPLATE=hype OUTPUT=final.mp4
```

Makefile variables (all overridable): `VIDEO` (default `test.mp4`), `TEMPLATE` (default `minimalist`), `SUBS` (default `<video>.subs.json`), `OUTPUT` (default `<video>.captioned.mp4`).

Alternative: `--transcription-preview` on `pycaps render` opens an interactive GUI editor after transcription, before rendering (one step, no manual JSON editing).

### `pycaps render` — main parameters

| Flag | Description |
|---|---|
| `--input <file>` | Input video (required) |
| `--output <file>` | Output video name (default: auto-generated) |
| `--template <name>` | Template to use (see list below) |
| `--config <file>` | JSON config file instead of/on top of a template |
| `--layout-align <top\|center\|bottom>` | Vertical position of subtitles (default `bottom`) |
| `--layout-align-offset <float>` | Nudge: `-1.0` (up) … `1.0` (down) |
| `--style <k=v>` | Override template styles, e.g. `--style word.color=red` |
| `--lang <code>` | Audio language, e.g. `--lang pl` |
| `--whisper-model <size>` | `tiny` / `base` (default) / `small` / `medium` / `large` |
| `--whisper-prompt <text>` | Vocabulary hints for Whisper (brand names, jargon) |
| `--transcript <file>` | Use an external transcript (`srt`/`vtt`/`whisper_json`/`pycaps_json`); skips Whisper, still runs processing |
| `--transcript-format <fmt>` | Force transcript format (default `auto`) |
| `--subtitle-data <file>` | Use processed pycaps JSON; skips transcription AND processing (for re-renders/corrections) |
| `--transcription-preview` | Pause after transcription and open an editable GUI preview |
| `--preview` | Fast low-quality render |
| `--preview-time <a,b>` | Render only seconds `a`–`b` (e.g. `10,15`) |
| `--video-quality <q>` | `low` / `middle` / `high` / `very_high` |
| `--verbose` / `-v` | Verbose logging |

Note: after every render pycaps automatically saves the subtitle data JSON next to the output video (`output.mp4` → `output.json`) — you can reuse it with `--subtitle-data`.

### Available templates

`default`, `minimalist`, `classic`, `fast`, `hype`, `explosive`, `vibrant`, `model`, `neo-minimal`, `retro-gaming`, `line-focus`, `word-focus`

Each template lives in `src/pycaps/template/preset/<name>/` — its CSS is in `styles.css` there (editable in place, since the install is editable). List them anytime with `make templates` or `pycaps template list`; preview styles with `pycaps preview-styles --template <name>`.

### Using as a Python library

```python
from pycaps import CapsPipelineBuilder

pipeline = (
    CapsPipelineBuilder()
    .with_input_video("input.mp4")
    .add_css("style.css")
    .build()
)
pipeline.run()
```

## Notes

- **The first render** downloads a Whisper model (a few hundred MB, one-time).
- **CPU transcription** on an Intel Mac is slow — for longer videos use a smaller Whisper model or provide a ready transcript via `--transcript`.
- Detailed docs: the [`docs/`](./docs) directory (`CLI.md`, `TEMPLATES.md`, `CONFIG_REFERENCE.md`, `EXAMPLES.md`).

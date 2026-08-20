# CLAUDE.md

## What this repo is

A fork of **pycaps** (Python tool for burning CSS-styled subtitles into videos, Whisper-based transcription) used primarily as a **personal workflow for captioning short Polish videos** (TikTok/Reels/Shorts format). The library source lives in `src/pycaps/`; the personal tooling on top of it is `Makefile`, `scripts/` and the local template folders.

Read `LAUNCH.md` first — it documents setup, all `pycaps render` parameters and available templates.

## How to help the user

- The user speaks Polish; the videos are in Polish (`--lang pl` if transcription quality is off).
- **The user prefers to run long-running or interactive commands themselves** (renders, GUI editors, logins). Prepare and hand over the exact command instead of executing it, unless explicitly asked to run it.
- Verify render results by extracting a frame: `ffmpeg -y -v error -ss <sec> -i out.mp4 -frames:v 1 frame.png` and reading the image.

## Environment

- Intel Mac (x86_64). Python venv at `.venv` (Python 3.12 via `uv`) — system Python 3.14 is NOT supported by pycaps.
- Everything runs through `.venv/bin/...` or `make` targets; `pycaps` is not on PATH.
- `make setup` builds the env. Do not "fix" the dependency pins in the Makefile: `numba==0.60.0`/`llvmlite==0.43.0` (newer have no x86_64 mac wheels) and `numpy<2` (torch 2.2.2, last Intel build, breaks with numpy 2).

## Subtitle creation flow

```bash
make subs VIDEO=film.mp4            # 1. transcribe only -> film.subs.json (no render)
make subs-edit VIDEO=film.mp4       #    ...or transcribe + GUI editor in one step
make edit SUBS=film.subs.json       # 2. correct subtitles in the GUI editor (repeatable)
make render VIDEO=film.mp4 TEMPLATE=<t>         # 3a. render (same template as in step 1)
make render-reflow VIDEO=film.mp4 TEMPLATE=<t>  # 3b. render, recalculating line breaks
```

- `render` uses `--subtitle-data` (JSON taken 1:1, including line breaks).
- `render-reflow` uses `--transcript --transcript-format pycaps_json` — keeps texts/timings but re-splits lines. **Required when rendering with a different template/font size than the one used for `make subs`**, otherwise lines overflow the frame.
- Defaults: `SUBS=<video>.subs.json`, `OUTPUT=<video>.captioned.mp4`.

## Templates

- Local (in repo root, take precedence): `it-caps` (VS Code-look tiles, embedded Montserrat), `explosive-caps` (glowing letters, 20px, subtitles at 3/4 height).
- Built-ins live in `src/pycaps/template/preset/<name>/` (`styles.css` + `pycaps.template.json`). List: `make templates`.
- To create a new template: copy a preset folder into the repo root and edit it — pycaps resolves template names against cwd first.
- Vertical position: `layout.vertical_align` in the template JSON, or `--layout-align` / `--layout-align-offset` flags. Math: `center` → y = height × (offset + 0.5), so 3/4 from top = center + 0.25.

## Gotchas (learned the hard way)

- **pycaps refuses to overwrite the output file.** Make targets `rm -f $(OUTPUT)` first; raw CLI calls must delete it manually.
- **Word states must not differ in anything width-affecting** (font-weight, font-size, letter-spacing, padding) when the template uses a proportional font. Each word slot gets the width of its widest state — a bolder `.word-being-narrated` leaves visible gaps between word tiles. Highlight with color/background/shadow only. (Monospace presets get away with bold; that's why `neo-minimal` worked and Montserrat didn't.)
- **The stock GUI editor hangs on Save** (pywebview destroy deadlock on macOS + lingering WebKit threads). `scripts/safe_editor.py` patches it; it is applied in `make edit` and `make subs-edit`. Avoid raw `pycaps render --transcription-preview` — it uses the unpatched editor. If a hung process lingers, find it with `ps aux | grep -E "edit_subs|bin/pycaps"` and kill it.
- Fonts not installed on the system must be embedded in the template CSS as base64 `@font-face` (see `it-caps/styles.css`) — the Playwright renderer won't find them otherwise. Montserrat variable TTF covers Polish diacritics.
- Changing template CSS invalidates the word-render cache — the next render is ~2-3x slower; that's normal.
- Every render also writes `<output>.json` (subtitle data) next to the video — reusable with `--subtitle-data`.
- Working artifacts (`*.subs.json`, `*.captioned.json`, `*.mp4`, `output_*.json`) are gitignored — commit only tooling, docs and templates.

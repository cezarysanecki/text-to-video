"""Generate pycaps subtitle data JSON without rendering the video.

Runs transcription + processing only and saves the subtitle data JSON,
which can be manually corrected and then passed to rendering via
`pycaps render --subtitle-data <file>.json`.
"""

import argparse
import os
from pathlib import Path

from pycaps import TemplateLoader

import safe_editor


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("video", help="Input video file")
    parser.add_argument("--template", default="default", help="Template name (affects segment splitting/layout)")
    parser.add_argument("--lang", default=None, help="Audio language, e.g. 'pl'")
    parser.add_argument("--whisper-model", default="base", help="Whisper model size (tiny/base/small/medium/large)")
    parser.add_argument("--edit", action="store_true", help="Open the GUI transcription editor before saving the JSON")
    args = parser.parse_args()

    if args.edit:
        safe_editor.apply()

    stem = Path(args.video).with_suffix("")
    output_stub = f"{stem}.subs.mp4"  # no video is written; only the .json next to it

    builder = TemplateLoader(args.template).with_input_video(args.video).load(False)
    builder.with_output_video(output_stub)
    builder.with_whisper_config(language=args.lang, model_size=args.whisper_model)
    builder.should_preview_transcription(args.edit)

    pipeline = builder.build()
    try:
        pipeline.prepare()
        document = pipeline.transcribe()
        pipeline.process_document(document)  # saves subtitle data to <output>.json
    finally:
        pipeline.close()

    print(f"\nSubtitle data saved to: {stem}.subs.json")
    print("Edit it, then render with:")
    print(f"  pycaps render --input {args.video} --template {args.template} --subtitle-data {stem}.subs.json")

    if args.edit:
        # WebKit threads from pywebview can keep the process alive after the
        # editor window closes — force a clean exit once everything is saved.
        os._exit(0)


if __name__ == "__main__":
    main()

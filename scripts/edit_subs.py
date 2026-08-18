"""Open the GUI subtitle editor for an existing pycaps subtitle data JSON.

Loads the JSON, lets you edit it in the graphical editor, and saves the
corrected version back to the same file. No transcription, no rendering.
"""

import argparse
import os

from pycaps.pipeline.subtitle_data_service import SubtitleDataService
from pycaps.tag import StructureTagger
from pycaps.transcriber import TranscriptionEditor

import safe_editor


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("subs", help="Subtitle data JSON file (e.g. test.subs.json)")
    args = parser.parse_args()

    service = SubtitleDataService(args.subs)
    document = service.load()

    safe_editor.apply()
    edited = TranscriptionEditor().run(document)

    # Structural tags depend on word positions, so reapply after editing
    # (mirrors what CapsPipeline does after its transcription preview)
    tagger = StructureTagger()
    tagger.clear(edited)
    tagger.tag(edited)

    service.save(edited)
    print(f"Saved: {args.subs}")
    # WebKit threads from pywebview can keep the process alive after the
    # window closes — force a clean exit once the file is written.
    os._exit(0)


if __name__ == "__main__":
    main()

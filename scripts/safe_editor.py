"""Workaround for the pycaps GUI editor hanging after Save/Cancel on macOS.

The stock editor destroys the pywebview window from inside the JS API
callback, which can deadlock the Cocoa event loop. This patch defers the
destroy to a background thread so the JS call returns first.
"""

import threading
import time

from pycaps.common import Document
from pycaps.transcriber.editor import transcription_editor as te


def _deferred_destroy() -> None:
    import webview

    time.sleep(0.2)
    if webview.active_window():
        webview.active_window().destroy()


def apply() -> None:
    def save(self, document_dict: dict) -> None:
        self._result_document = Document.from_dict(document_dict)
        threading.Thread(target=_deferred_destroy, daemon=True).start()

    def cancel(self) -> None:
        self._result_document = None
        threading.Thread(target=_deferred_destroy, daemon=True).start()

    te._Api.save = save
    te._Api.cancel = cancel

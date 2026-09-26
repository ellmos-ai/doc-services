# SPDX-License-Identifier: MIT
"""Regressionstests für die OCR-Konfidenzauswertung."""

from __future__ import annotations

import sys
from types import SimpleNamespace

import pytest

from doc_services.ocr import _erkenne_bild


def test_erkenne_bild_mittelt_dezimale_konfidenzen(monkeypatch):
    """Tesseract-Dezimalwerte werden gemittelt, Platzhalter ignoriert."""
    pytesseract = SimpleNamespace(
        Output=SimpleNamespace(DICT="dict"),
        image_to_string=lambda bild, lang: " erkannter Text ",
        image_to_data=lambda bild, lang, output_type: {
            "conf": ["-1", "-1.0", "95.5", 84, "", None, "nan", "inf"],
        },
    )
    monkeypatch.setitem(sys.modules, "pytesseract", pytesseract)

    text, konfidenz = _erkenne_bild(object(), "deu+eng")

    assert text == "erkannter Text"
    assert konfidenz == pytest.approx(89.75)

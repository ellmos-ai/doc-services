# SPDX-License-Identifier: MIT
"""OCR fuer Bilder und PDFs - ohne AGPL-Bindung.

Herkunft: portiert aus BACH `system/tools/ocr/engine.py` (MIT, eigenes Copyright).

DER ENTSCHEIDENDE UNTERSCHIED ZUR BACH-FASSUNG:
BACH rendert PDF-Seiten mit PyMuPDF (`fitz`) - im dortigen Code selbst als
"PyMuPDF optional (AGPL)" markiert. Das ist geerbte Copyleft, die wirklich
bindet und die Auslieferung eines Moduls blockiert. Hier laeuft das Rendering
ausschliesslich ueber **pypdfium2** (BSD-3-Clause / Apache-2.0).

`fitz` wird in diesem Paket nirgends importiert. Der Test
tests/test_no_agpl.py haelt das dauerhaft fest.

Entscheidung E08 vom 2026-08-18.
"""

from __future__ import annotations

import shutil
import sys
from dataclasses import dataclass
from math import isfinite
from pathlib import Path

STANDARD_SPRACHE = "deu+eng"
OCR_RENDER_DPI = 300


class OCRNichtVerfuegbar(RuntimeError):
    """Tesseract oder eine Renderer-Abhaengigkeit fehlt."""


@dataclass
class SeitenErgebnis:
    seite: int
    text: str
    konfidenz: float
    woerter: int


@dataclass
class OCRErgebnis:
    text: str
    konfidenz: float
    sprache: str
    seiten: list[SeitenErgebnis]

    @property
    def woerter(self) -> int:
        return len(self.text.split())


# ----------------------------------------------------------------------------
# Verfuegbarkeit
# ----------------------------------------------------------------------------

def _tesseract_pfad() -> str | None:
    """Findet Tesseract: PATH, Standardinstallation, portable Kopie."""
    if (gefunden := shutil.which("tesseract")):
        return gefunden
    if sys.platform == "win32":
        standard = Path(r"C:\Program Files\Tesseract-OCR\tesseract.exe")
        if standard.exists():
            return str(standard)
    return None


def verfuegbarkeit() -> dict[str, bool | str]:
    """Was fehlt konkret? Wird im Fehlerfall angezeigt statt eines nackten 'geht nicht'."""
    lage: dict[str, bool | str] = {}
    try:
        import pytesseract  # noqa: F401
        lage["pytesseract"] = True
    except ImportError:
        lage["pytesseract"] = False
    try:
        from PIL import Image  # noqa: F401
        lage["pillow"] = True
    except ImportError:
        lage["pillow"] = False
    try:
        import pypdfium2  # noqa: F401
        lage["pypdfium2"] = True
    except ImportError:
        lage["pypdfium2"] = False
    pfad = _tesseract_pfad()
    lage["tesseract"] = bool(pfad)
    lage["tesseract_pfad"] = pfad or "nicht gefunden"
    return lage


def _sicherstellen(pdf: bool = False) -> None:
    lage = verfuegbarkeit()
    fehlt = [k for k in ("pytesseract", "pillow", "tesseract") if not lage[k]]
    if pdf and not lage["pypdfium2"]:
        fehlt.append("pypdfium2")
    if fehlt:
        raise OCRNichtVerfuegbar(
            "OCR nicht moeglich, es fehlt: " + ", ".join(fehlt)
            + ". Installation: pip install pytesseract pillow pypdfium2 "
            + "und Tesseract-OCR (mit Sprachpaket 'deu')."
        )


# ----------------------------------------------------------------------------
# Erkennung
# ----------------------------------------------------------------------------

def _erkenne_bild(bild, sprache: str):
    import pytesseract
    text = pytesseract.image_to_string(bild, lang=sprache)
    daten = pytesseract.image_to_data(bild, lang=sprache,
                                      output_type=pytesseract.Output.DICT)
    werte: list[float] = []
    for rohwert in daten["conf"]:
        try:
            wert = float(rohwert)
        except (TypeError, ValueError):
            continue
        if wert != -1.0 and isfinite(wert):
            werte.append(wert)
    return text.strip(), (sum(werte) / len(werte) if werte else 0.0)


def ocr_bild(pfad: Path | str, sprache: str = STANDARD_SPRACHE) -> OCRErgebnis:
    _sicherstellen()
    from PIL import Image
    pfad = Path(pfad)
    tesser = _tesseract_pfad()
    if tesser:
        import pytesseract
        pytesseract.pytesseract.tesseract_cmd = tesser
    with Image.open(pfad) as bild:
        text, konf = _erkenne_bild(bild, sprache)
    seite = SeitenErgebnis(1, text, konf, len(text.split()))
    return OCRErgebnis(text=text, konfidenz=konf, sprache=sprache, seiten=[seite])


def ocr_pdf(pfad: Path | str, sprache: str = STANDARD_SPRACHE,
            seiten: list[int] | None = None, dpi: int = OCR_RENDER_DPI) -> OCRErgebnis:
    """Rendert PDF-Seiten mit pypdfium2 und erkennt sie einzeln.

    Bewusst KEIN PyMuPDF - siehe Modul-Docstring.
    """
    _sicherstellen(pdf=True)
    import pypdfium2 as pdfium
    from PIL import Image  # noqa: F401  (pypdfium2 liefert PIL-Bilder)

    tesser = _tesseract_pfad()
    if tesser:
        import pytesseract
        pytesseract.pytesseract.tesseract_cmd = tesser

    pfad = Path(pfad)
    dok = pdfium.PdfDocument(str(pfad))
    try:
        indizes = [s - 1 for s in seiten] if seiten else range(len(dok))
        ergebnisse: list[SeitenErgebnis] = []
        for idx in indizes:
            if idx < 0 or idx >= len(dok):
                continue
            seite = dok[idx]
            # pypdfium2 skaliert ueber einen Faktor relativ zu 72 dpi
            bild = seite.render(scale=dpi / 72).to_pil()
            text, konf = _erkenne_bild(bild, sprache)
            ergebnisse.append(SeitenErgebnis(idx + 1, text, konf, len(text.split())))
    finally:
        dok.close()

    volltext = "\n\n".join(e.text for e in ergebnisse if e.text)
    mittel = (sum(e.konfidenz for e in ergebnisse) / len(ergebnisse)) if ergebnisse else 0.0
    return OCRErgebnis(text=volltext, konfidenz=mittel, sprache=sprache, seiten=ergebnisse)


def ocr_datei(pfad: Path | str, sprache: str = STANDARD_SPRACHE) -> str:
    """Bequemer Einstieg fuer die Extraktionskette: liefert nur den Text."""
    pfad = Path(pfad)
    endung = pfad.suffix.lower()
    if endung == ".pdf":
        return ocr_pdf(pfad, sprache).text
    if endung in {".jpg", ".jpeg", ".png", ".tif", ".tiff", ".bmp"}:
        return ocr_bild(pfad, sprache).text
    raise OCRNichtVerfuegbar(f"OCR fuer '{endung}' nicht vorgesehen.")


def hat_textebene(pfad: Path | str, mindestzeichen: int = 40) -> bool:
    """Hat das PDF bereits eine Textebene? Dann ist OCR unnoetig und schaedlich.

    Spart Rechenzeit und vermeidet, dass sauberer Text durch OCR-Rauschen
    ersetzt wird.
    """
    try:
        from pypdf import PdfReader
    except ImportError:
        return False
    try:
        reader = PdfReader(str(pfad))
        zeichen = sum(len((s.extract_text() or "").strip()) for s in reader.pages[:5])
        return zeichen >= mindestzeichen
    except Exception:
        return False

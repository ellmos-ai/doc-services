# SPDX-License-Identifier: MIT
"""doc-services — Dokumentenextraktion, OCR und Datenschutzpruefung.

BACH-unabhaengige Herausloesung der Dokumentendienste aus
`BACH/system/hub/_services/document/` (MIT, eigenes Copyright).

Drei Bausteine:
  extract   Datei -> Text/Markdown ueber eine konfigurierbare Praeferenzkette
            mit ehrlichem Fallback. Enthaelt den Fix fuer verbundene
            Tabellenzellen (Ticket T-20260817-05).
  ocr       Tesseract fuer Bilder und PDFs, Rendering ueber pypdfium2.
            KEIN PyMuPDF - siehe doc_services/ocr.py.
  privacy   Inhaltsbasierte Ampelpruefung vor Weitergabe an Dritte.

  config    Praeferenz- und Lernschicht: profil.json (Katalog) + config.json
            (unsere Lage). Siehe doc_services/config.py.

Entscheidungsgrundlage: E01-E08 vom 2026-08-18,
_control-center/_DECISIONS/DECISION-BRIEFING_caveman-markitdown_2026-08-17.md
"""

from .config import Auswahl, BackendLage, Registry, registry
from .extract import (
    AUSGABEFORMEN,
    SUFFIX_MAP,
    Ergebnis,
    ExtraktionsFehler,
    extrahieren,
    format_von,
)
from .privacy import (
    GELB,
    GRUEN,
    ROT,
    Befund,
    Klassifikator,
    darf_weitergegeben_werden,
)

__version__ = "0.1.1"

__all__ = [
    "Registry", "registry", "BackendLage", "Auswahl",
    "Ergebnis", "ExtraktionsFehler", "extrahieren", "format_von", "SUFFIX_MAP",
    "AUSGABEFORMEN",
    "Befund", "Klassifikator", "darf_weitergegeben_werden", "ROT", "GELB", "GRUEN",
    "__version__",
]

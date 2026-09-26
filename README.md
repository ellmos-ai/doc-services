<img src="assets/banner.png" width="100%" alt="doc-services banner">

# doc-services

[![Python 3.10+](https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13-blue.svg)](pyproject.toml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![CI](https://img.shields.io/badge/CI-passing-brightgreen.svg)](.github/workflows/ci.yml)
[![Egress: Zero](https://img.shields.io/badge/Egress-Zero%20(Local--First)-success.svg)](SECURITY.md)
[![Execution: RunAsInvoker](https://img.shields.io/badge/Execution-RunAsInvoker-blue.svg)](SECURITY.md)

**Document extraction, OCR and privacy screening — BACH-independent, permissively licensed, with a learning backend preference.**

English · [Deutsch](README_de.md) · [Security Policy](SECURITY.md) · [LLM Context Index](llms.txt) · [Changelog](CHANGELOG.md) · [Marketing Log](MARKETING-LOG.txt)

---

## Why

An agent that has to read documents faces three questions: *which tool* handles this format,
*what happens* when that tool is missing, and *may* this content be passed on at all. This
module answers all three in one place.

Extracted from `BACH/system/hub/_services/document/` (MIT, own copyright) and decoupled from
BACH: no imports from `hub`/`tools`, no SQLite coupling, no client-record logic.

## The building blocks

| Module | Purpose |
|---|---|
| `extract` | File → text/Markdown through a preference chain with honest fallback |
| `ocr` | Tesseract for images and PDFs, rendering via **pypdfium2** |
| `privacy` | Content-based traffic-light screening before handing data to third parties |
| `config` | Catalogue (`profil.json`) + local situation (`config.json`), learning |

## Two deliberate differences

**1. Merged table cells are no longer duplicated.**
`python-docx` returns a cell merged across several columns *once per grid column*. Without
deduplication it lands in the text that many times. Measured on a real 25 KB file: **785 counted
versus 44 unique cells** — a factor of 17.8, roughly **12,750 wasted tokens** in a single file.
This module deduplicates via the identity of the underlying `tc` XML element. (`id(cell)` is not
enough — python-docx creates fresh wrapper objects on every access.)

**2. No AGPL entanglement.**
PDF rendering goes exclusively through `pypdfium2` (BSD-3-Clause / Apache-2.0). PyMuPDF (`fitz`,
AGPL) is imported nowhere. `tests/test_no_agpl.py` enforces this — a test rather than a note,
because a note stops nobody.

## Learning preference instead of hard wiring

Two files with distinct roles:

- **`profil.json`** — catalogue: what *theoretically exists* for a format, with strengths,
  weaknesses and licence. It also knows backends that are not installed here.
- **`config.json`** — our situation: what is *installed*, what we *prefer*, what is disabled,
  plus the recorded track record.

```python
from doc_services import registry, extrahieren

reg = registry()
print(reg.lagebericht())          # what we know, what we have, what we use

reg.setze_praeferenz("xlsx", ["openpyxl-native", "markitdown"])   # preferred, then fallback
reg.speichern()

result = extrahieren("report.docx")
print(result.backend, result.produces, result.zeichen)
```

### Asking for an output form: `produces`

Callers that **process** the text rather than display it -- redaction, search, rules on word
boundaries -- need plain text, not Markdown decoration:

```python
e = extrahieren("paper.pdf", produces="text")   # chain kept, narrowed to text backends
```

For LaTeX PDFs this is not a matter of taste. Measured on a real paper (2026-09-13):
markitdown returns **8,698 words instead of 14,856**, and 37% of its tokens do not occur in
the `.tex` source at all -- whole sentences glue into a single token because the word spacing
is lost. With `produces="text"` the result matches `pypdf` byte for byte.

`produces` **narrows** the preference chain, it does not replace it: fallbacks of the same
output form are kept. That is the difference from `nur_backend`, which pins exactly one
backend and loses every fallback.

**Learning does not mean the order silently changes.** Successes and failures are counted and
surfaced; `umsortierung_vorschlagen()` *proposes* a reordering, a human decides. Silent
self-rewiring would be the wrong behaviour in a chain that feeds documents to an LLM.

## Privacy: content, not filename

```python
from doc_services import darf_weitergegeben_werden

allowed, verdict = darf_weitergegeben_werden("files/note.md")
if not allowed:
    print(verdict.bericht())
```

A guard that only inspects filenames misses credentials in innocuously named files — demonstrated
with `CREDENTIALS/<provider>/webhosting.md`, which a pure name filter lets through. This module
therefore inspects **content** (IBAN, tax ID, social security number, health data, private keys,
API tokens) and uses path patterns only *in addition*.

The default is **fail-closed**: RED and YELLOW block. Matches are masked in the report — a report
that leaks the secret would defeat its purpose.

## Install

```bash
pip install -e ".[all]"                      # everything
pip install -e ".[markitdown,office,pdf]"    # without OCR
```

There are deliberately no hard dependencies: the module detects at runtime what is present and
reports what is missing **with a reason** rather than a bare failure.

OCR additionally requires Tesseract with the German language pack.

## Tests

```bash
pytest -ra -v
```

Full unit and contract test suites cover zero-copyleft guarantees, cell deduplication, privacy screening, backend fallbacks, and repository hygiene.


## Provenance

Result of decisions E01–E08 of 2026-08-18. The merged-cell fix is ticket `T-20260817-825816579`,
the licence change is decision E08.

**Licence:** MIT

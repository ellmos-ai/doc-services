# SPDX-License-Identifier: MIT
"""Execute the documented DOCX privacy recipes against real extracted content."""

from pathlib import Path

import pytest


@pytest.mark.parametrize(
    ("readme", "filename", "allowed_name"),
    [
        ("README.md", "project_notes.docx", "allowed"),
        ("README_de.md", "notizen.docx", "erlaubt"),
    ],
)
@pytest.mark.parametrize("sensitive", [False, True])
def test_documented_docx_privacy_recipe(
    tmp_path, monkeypatch, capsys, readme, filename, allowed_name, sensitive
):
    docx = pytest.importorskip("docx")
    document = docx.Document()
    document.add_paragraph(
        "IBAN DE89370400440532013000" if sensitive else "A simple public project note."
    )
    document.save(tmp_path / filename)
    text = (Path(__file__).resolve().parent.parent / readme).read_text(encoding="utf-8")
    section = text.split('<a id="sec-10"></a>', 1)[1].split('<a id="sec-11"></a>', 1)[0]
    recipe = section.split("```python\n", 1)[1].split("```", 1)[0]
    monkeypatch.chdir(tmp_path)
    namespace = {}
    exec(compile(recipe, readme, "exec"), namespace)
    assert namespace[allowed_name] is (not sensitive)
    if sensitive:
        assert "ROT" in capsys.readouterr().out

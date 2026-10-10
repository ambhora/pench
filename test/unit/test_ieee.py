# SPDX-License-Identifier: Apache-2.0
# Copyright (C) 2026 Pench contributors
"""Regression tests for IEEE conference scaffolding."""

from pathlib import Path
import os
import shutil
import subprocess

import pytest

import pench.cli
import pench.tex
import pench.tex.license
import pench.tex.template
from conftest import SHARE_DIR


def _create_ieee(dir_info, tmp_path, **overrides):
    args = {
        "tex_subcommand": "create",
        "doctype": "ieee-conference",
        "outdir": str(tmp_path),
        "title": "HPC & Data at 100%",
        "author": "Jane Doe",
        "email": "jane@example.org",
        "affiliation": "Example R&D Institute",
        "abstract": "Experiments on A&B at 100% occupancy.",
        "keywords": "HPC, R&D, 100%",
        "license": "CC-BY-4.0",
        "parsable": True,
    }
    args.update(overrides)
    return Path(pench.tex.execute(dir_info, args))


def test_ieee_source_metadata_and_bibliography(dir_info, tmp_path, capsys):
    project = _create_ieee(dir_info, tmp_path)
    capsys.readouterr()
    slug = "hpc-data-at-100"
    main = (project / f"{slug}.tex").read_text(encoding="utf-8")
    bib = (project / "references.bib").read_text(encoding="utf-8")
    makefile = (project / "makefile").read_text(encoding="utf-8")

    assert r"\documentclass[conference]{IEEEtran}" in main
    assert r"\title{HPC \& Data at 100\%}" in main
    assert r"\textit{Example R\&D Institute}" in main
    assert r"Experiments on A\&B at 100\% occupancy." in main
    assert r"HPC, R\&D, 100\%" in main
    assert r"\bibliographystyle{IEEEtran}" in main
    assert r"\bibliography{references}" in main
    assert r"\RequirePackage{penchcommon}" not in main
    assert r"\usepackage{geometry}" not in main
    assert "@@" not in main
    assert "@book{lamport1994latex," in bib
    assert "@comment{ SPDX-License-Identifier: CC-BY-4.0 }" in bib
    assert "jane@example.org" not in bib.splitlines()[:2]
    assert "BFLAGS=-pdf" in makefile
    assert "-shell-escape" not in makefile
    assert (project / "README.md").is_file()
    workflow = (project / ".github/workflows/build.yml").read_text()
    assert "hpc-data-at-100.pdf" in workflow
    assert (project / "texmf/tex/latex/ieeetran/IEEEtran.cls").is_file()
    assert (project / "texmf/bibtex/bst/ieeetran/IEEEtran.bst").is_file()
    assert (project / "texmf/bibtex/bst/ieeetran/IEEEtranS.bst").is_file()


def test_ieee_upstream_assets_are_copied_unchanged(dir_info, tmp_path, capsys):
    project = _create_ieee(dir_info, tmp_path)
    capsys.readouterr()
    for name in [
        "tex/latex/ieeetran/IEEEtran.cls",
        "bibtex/bst/ieeetran/IEEEtran.bst",
        "bibtex/bst/ieeetran/IEEEtranS.bst",
        "bibtex/bib/ieeetran/IEEEabrv.bib",
    ]:
        src = Path(SHARE_DIR) / "texmf" / name
        dst = project / "texmf" / name
        assert dst.read_bytes() == src.read_bytes()


def test_ieee_cli_from_installed_share(tmp_path, monkeypatch, capsys):
    monkeypatch.setenv("PENCH_SHARE_DIR", SHARE_DIR)
    result = pench.cli.run([
        "tex", "create", "--doctype", "ieee-conference",
        "--title", "Test IEEE", "--author", "Jane Doe",
        "--email", "jane@example.org", "--license", "MIT",
        "--outdir", str(tmp_path), "--parsable",
    ])
    assert result == 0
    assert capsys.readouterr().out.strip() == str(tmp_path / "test-ieee")


def test_common_pench_documents_remain_lualatex(dir_info, base_args):
    project = Path(pench.tex.execute(dir_info, base_args))
    makefile = (project / "makefile").read_text()
    assert "BFLAGS=-lualatex" in makefile
    assert "-shell-escape" not in makefile
    assert "@book{knuth1984texbook," in (project / "references.bib").read_text()


def test_ieee_no_vendor_option(dir_info, tmp_path, capsys):
    project = _create_ieee(dir_info, tmp_path, no_vendor_texmf=True)
    capsys.readouterr()
    assert not (project / "texmf").exists()
    assert (project / "references.bib").is_file()


def test_ieee_bibtex_header_no_unescaped_at_character():
    header = pench.tex.license.header_for_file("MIT", "Jane Doe", "jane@example.org", "refs.bib")
    assert "@comment{ SPDX-License-Identifier: MIT }" in header
    assert header.count("@") == 2


@pytest.mark.skipif(os.environ.get("PENCH_LATEX_SMOKE") != "1",
                    reason="Set PENCH_LATEX_SMOKE=1 for the optional TeX integration test")
def test_ieee_compiles_with_bibtex(dir_info, tmp_path, capsys):
    if not shutil.which("latexmk") or not shutil.which("bibtex"):
        pytest.skip("latexmk and BibTeX are needed for this integration test")
    project = _create_ieee(dir_info, tmp_path)
    capsys.readouterr()
    p = subprocess.run(["make", "verbose"], cwd=project,
                       stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                       text=True, timeout=120)
    assert p.returncode == 0, p.stdout[-8000:]
    assert (project / "hpc-data-at-100.pdf").is_file()
    bbl = (project / "tmp/build/hpc-data-at-100.bbl").read_text()
    assert "Lamport" in bbl

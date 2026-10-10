# --------------------------------------------------------------------------------------------------
# SPDX-License-Identifier: Apache-2.0
# Copyright (C) 2025 Jayesh Badwaik <jayesh@ambhora.com>
# --------------------------------------------------------------------------------------------------

import pytest

import pench.tex.license as license_module


@pytest.mark.parametrize(
    "filename,expected",
    [
        ("paper.tex", "tex"),
        ("makefile", "makefile"),
        (".latexmkrc", "perl"),
        (".gitlab-ci.yml", "yaml"),
        (".gitignore", "gitignore"),
        ("readme.md", "markdown"),
    ],
)
def test_filetype_for(filename, expected):
    assert license_module.filetype_for(filename) == expected


def test_filetype_for_rejects_unknown():
    with pytest.raises(license_module.UnknownFileTypeError):
        license_module.filetype_for("mystery.zzz")


def test_line_header_uses_comment_char():
    header = license_module.header("MIT", "Jane Doe", "jane@example.com", "tex")
    assert header.startswith("% ---")
    assert "SPDX-License-Identifier: MIT" in header
    assert "Jane Doe <jane@example.com>" in header


def test_block_header_for_markdown():
    header = license_module.header("MIT", "Jane Doe", "jane@example.com", "markdown")
    assert header.startswith("<!--")
    assert header.rstrip().endswith("-->")


def test_header_rejects_unknown_filetype():
    with pytest.raises(license_module.UnknownFileTypeError):
        license_module.header("MIT", "Jane Doe", "jane@example.com", "cobol")


def test_header_for_file_infers_syntax():
    header = license_module.header_for_file("MIT", "Jane Doe", "jane@example.com", "makefile")
    assert header.startswith("# ---")

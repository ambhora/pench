# --------------------------------------------------------------------------------------------------
# SPDX-License-Identifier: Apache-2.0
# Copyright (C) 2025 Jayesh Badwaik <jayesh@ambhora.com>
# --------------------------------------------------------------------------------------------------

import pytest

import pench.tex.template as template


def test_render_substitutes_placeholders():
    assert template.render("@@a@@ and @@b@@", {"a": "x", "b": "y"}) == "x and y"


def test_render_rejects_undefined_placeholder():
    with pytest.raises(template.TemplateError, match="missing_one"):
        template.render("@@missing_one@@", {})


def test_render_leaves_tex_math_and_braces_alone():
    body = r"$x^2$ \title{Hello} ${TITLE}"
    assert template.render(body, {}) == body


def test_placeholders():
    assert template.placeholders("@@a@@ @@b@@ @@a@@") == {"a", "b"}


@pytest.mark.parametrize(
    "raw,expected",
    [
        ("R&D", r"R\&D"),
        ("100%", r"100\%"),
        ("a_b", r"a\_b"),
        ("#1", r"\#1"),
        ("{x}", r"\{x\}"),
        ("plain", "plain"),
    ],
)
def test_latex_escape(raw, expected):
    assert template.latex_escape(raw) == expected


@pytest.mark.parametrize(
    "source,expected",
    [
        ("makefile.in", "makefile"),
        ("dot-latexmkrc.in", ".latexmkrc"),
        ("dot-gitlab-ci.yml.in", ".gitlab-ci.yml"),
        ("dot-github", ".github"),
        ("main.tex.in", "main.tex"),
    ],
)
def test_target_name(source, expected):
    assert template.target_name(source) == expected


def test_repository_discovers_installed_doctypes(dir_info):
    repository = template.TemplateRepository(dir_info)
    assert repository.available() == ["article", "book", "ieee-conference", "note"]
    assert repository.has("article")
    assert not repository.has("beamer")


def test_repository_rejects_uninstalled_doctype(dir_info):
    repository = template.TemplateRepository(dir_info)
    with pytest.raises(template.TemplateError, match="available: article, book, ieee-conference, note"):
        repository.main_template("beamer")


def test_repository_lists_common_files(dir_info):
    repository = template.TemplateRepository(dir_info)
    targets = sorted(target for _, target in repository.common_files())
    assert targets == [".github/workflows/build.yml", ".gitignore", ".gitlab-ci.yml",
                       ".latexmkrc", "makefile", "references.bib"]

# --------------------------------------------------------------------------------------------------
# SPDX-License-Identifier: Apache-2.0
# Copyright (C) 2025 Jayesh Badwaik <jayesh@ambhora.com>
# --------------------------------------------------------------------------------------------------

import os

import pytest

import pench.tex
import pench.tex.create as create_module


@pytest.mark.parametrize(
    "title,expected",
    [
        ("My Great Paper", "my-great-paper"),
        ("Hello,   World!", "hello-world"),
        ("Jayesh's Notes", "jayeshs-notes"),
        ("Über Größe", "uber-grosse"),  # NFKD strips the umlaut; ß has an explicit transliteration
        ("  spaced  out  ", "spaced-out"),
        ("Naïve Café", "naive-cafe"),
    ],
)
def test_sanitize_title(title, expected):
    assert create_module.sanitize_title(title) == expected


def test_sanitize_title_rejects_empty_result():
    with pytest.raises(ValueError, match="no characters usable"):
        create_module.sanitize_title("!!!")


@pytest.mark.parametrize(
    "author,expected",
    [
        ("Jayesh Badwaik", "JBAD-2025-0001"),
        ("Jane Q Doe", "JQDOE-2025-0001"),
        ("Prince", "PRIN-2025-0001"),
        ("", "DOC-2025-0001"),
    ],
)
def test_default_docid(author, expected):
    assert create_module.default_docid(author, year=2025) == expected


def test_missing_fields_reports_every_gap():
    assert set(create_module.missing_fields({"doctype": "article"})) == {
        "outdir", "title", "author", "license", "email"
    }


def test_create_without_interactive_names_missing_options(dir_info, base_args):
    del base_args["author"]
    del base_args["email"]
    with pytest.raises(ValueError, match=r"--author, --email"):
        pench.tex.execute(dir_info, base_args)


def test_execute_rejects_unknown_subcommand(dir_info, base_args):
    base_args["tex_subcommand"] = "bogus"
    with pytest.raises(ValueError, match="unknown tex subcommand: bogus"):
        pench.tex.execute(dir_info, base_args)


def test_create_generates_expected_tree(dir_info, base_args):
    projectdir = pench.tex.execute(dir_info, base_args)

    assert os.path.basename(projectdir) == "my-great-paper"
    for name in ["my-great-paper.tex", "makefile", ".latexmkrc", ".gitignore",
                 ".gitlab-ci.yml", ".github/workflows/build.yml", "texmf"]:
        assert os.path.exists(os.path.join(projectdir, name)), name

    assert os.path.isfile(
        os.path.join(projectdir, "texmf", "tex", "latex", "pench", "pencharticle.cls")
    )


def test_create_substitutes_metadata_into_document(dir_info, base_args):
    base_args["subtitle"] = "A Study"
    base_args["publishers"] = "Ambhora"
    base_args["date"] = "2025-06-01"
    projectdir = pench.tex.execute(dir_info, base_args)

    with open(os.path.join(projectdir, "my-great-paper.tex"), encoding="utf-8") as handle:
        body = handle.read()

    assert r"\title{My Great Paper}" in body
    assert r"\author{Jane Doe}" in body
    assert r"\subtitle{A Study}" in body
    assert r"\date{2025-06-01}" in body
    assert "license=CC-BY-4.0" in body
    assert "docid=JDOE-" in body
    assert "@@" not in body
    assert "Minimal Document" not in body
    assert "Someone Important" not in body


def test_create_escapes_tex_special_characters(dir_info, base_args):
    base_args["title"] = "R&D at 100% Capacity"
    projectdir = pench.tex.execute(dir_info, base_args)

    assert os.path.basename(projectdir) == "r-d-at-100-capacity"
    with open(os.path.join(projectdir, "r-d-at-100-capacity.tex"), encoding="utf-8") as handle:
        assert r"\title{R\&D at 100\% Capacity}" in handle.read()


def test_makefile_gets_slug_and_header(dir_info, base_args):
    projectdir = pench.tex.execute(dir_info, base_args)
    with open(os.path.join(projectdir, "makefile"), encoding="utf-8") as handle:
        body = handle.read()

    assert body.startswith("# ---")
    assert "TITLE=my-great-paper" in body
    assert "${TITLE}.tex" in body


def test_generated_files_have_one_license_header(dir_info, base_args):
    projectdir = pench.tex.execute(dir_info, base_args)
    for name in ["my-great-paper.tex", "makefile", ".gitlab-ci.yml", ".latexmkrc",
                 ".github/workflows/build.yml"]:
        with open(os.path.join(projectdir, name), encoding="utf-8") as handle:
            body = handle.read()
        assert body.count("SPDX-License-Identifier:") == 1, name
        assert "CC-BY-4.0" in body


def test_no_vendor_texmf_skips_the_tree(dir_info, base_args):
    base_args["no_vendor_texmf"] = True
    projectdir = pench.tex.execute(dir_info, base_args)
    assert not os.path.exists(os.path.join(projectdir, "texmf"))


def test_create_refuses_to_overwrite(dir_info, base_args):
    pench.tex.execute(dir_info, dict(base_args))
    with pytest.raises(FileExistsError, match="already exists"):
        pench.tex.execute(dir_info, dict(base_args))


def test_failed_generation_leaves_nothing_behind(dir_info, base_args):
    base_args["doctype"] = "article"
    projectdir = os.path.join(os.path.abspath(base_args["outdir"]), "my-great-paper")

    original = create_module.write_rendered

    def exploding(*args, **kwargs):
        raise RuntimeError("boom")

    create_module.write_rendered = exploding
    try:
        with pytest.raises(RuntimeError):
            pench.tex.execute(dir_info, base_args)
    finally:
        create_module.write_rendered = original

    assert not os.path.exists(projectdir)


def test_unknown_doctype_is_rejected(dir_info, base_args):
    base_args["doctype"] = "beamer"
    with pytest.raises(ValueError, match="unknown DocType 'beamer'"):
        pench.tex.execute(dir_info, base_args)


def test_user_input_is_json_serialisable(base_args):
    base_args["doctype"] = pench.tex.DocType.article
    user_input = pench.tex.UserInput(base_args)
    assert "My Great Paper" in str(user_input)
    assert "my-great-paper" in repr(user_input)


def test_docversion_flows_into_the_document(dir_info, base_args):
    base_args["docversion"] = "2.5"
    projectdir = pench.tex.execute(dir_info, base_args)
    with open(os.path.join(projectdir, "my-great-paper.tex"), encoding="utf-8") as handle:
        assert "version=2.5" in handle.read()


def test_generated_github_workflow_has_document_name(dir_info, base_args):
    projectdir = pench.tex.execute(dir_info, base_args)
    with open(os.path.join(projectdir, ".github", "workflows", "build.yml"),
              encoding="utf-8") as handle:
        workflow = handle.read()
    assert "name: 'my-great-paper-pdf'" in workflow
    assert "test -s 'my-great-paper.pdf'" in workflow
    assert "@@" not in workflow
    assert "uses: xu-cheng/texlive-action@22c04326" in workflow


def test_note_starter_has_no_disabled_sectioning_commands(dir_info, base_args):
    base_args["doctype"] = "note"
    project = pench.tex.execute(dir_info, base_args)
    with open(os.path.join(project, "my-great-paper.tex"), encoding="utf-8") as handle:
        document = handle.read()
    for command in ("section", "subsection", "subsubsection", "part"):
        assert "\\" + command + "{" not in document
    assert "\\printbibliography[heading=none]" in document

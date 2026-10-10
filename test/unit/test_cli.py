# --------------------------------------------------------------------------------------------------
# SPDX-License-Identifier: Apache-2.0
# Copyright (C) 2025 Jayesh Badwaik <jayesh@ambhora.com>
# --------------------------------------------------------------------------------------------------

import os

import pytest

import pench.cli
import pench.paths

from conftest import SHARE_DIR


@pytest.fixture(autouse=True)
def use_repo_share(monkeypatch):
    monkeypatch.setenv(pench.paths.SHARE_DIR_ENV, SHARE_DIR)


def test_parser_offers_discovered_doctypes():
    parser = pench.cli.top_level_parser(["article", "book", "note"])
    args = parser.parse_args(["tex", "create", "--doctype", "book"])
    assert args.doctype == "book"
    assert args.tex_subcommand == "create"


def test_parser_rejects_unknown_doctype(capsys):
    parser = pench.cli.top_level_parser(["article"])
    with pytest.raises(SystemExit):
        parser.parse_args(["tex", "create", "--doctype", "beamer"])
    assert "invalid choice" in capsys.readouterr().err


def test_run_creates_project(tmp_path, capsys):
    status = pench.cli.run([
        "tex", "create",
        "--doctype", "note",
        "--title", "Some Note",
        "--outdir", str(tmp_path),
        "--author", "Jane Doe",
        "--email", "jane@example.com",
        "--license", "MIT",
        "--parsable",
    ])
    assert status == 0

    printed = capsys.readouterr().out.strip()
    assert printed == str(tmp_path / "some-note")
    assert os.path.isfile(os.path.join(printed, "some-note.tex"))


def test_run_reports_missing_options(tmp_path, capsys):
    status = pench.cli.run([
        "tex", "create", "--doctype", "note", "--outdir", str(tmp_path),
    ])
    assert status == 1
    assert "missing required option(s)" in capsys.readouterr().err


def test_run_reports_existing_directory(tmp_path, capsys):
    argv = [
        "tex", "create", "--doctype", "note", "--title", "Some Note",
        "--outdir", str(tmp_path), "--author", "Jane Doe",
        "--email", "jane@example.com", "--license", "MIT", "--parsable",
    ]
    assert pench.cli.run(argv) == 0
    capsys.readouterr()
    assert pench.cli.run(argv) == 1
    assert "already exists" in capsys.readouterr().err


def test_run_reports_missing_share_dir(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(pench.paths, "_candidate_share_dirs", lambda binary_dir: [])
    assert pench.cli.run(["tex", "create"]) == 1
    assert "could not locate" in capsys.readouterr().err


def test_run_aborts_cleanly_on_eof(tmp_path, monkeypatch, capsys):
    def no_input(*args, **kwargs):
        raise EOFError

    monkeypatch.setattr("builtins.input", no_input)
    status = pench.cli.run(["tex", "create", "--outdir", str(tmp_path), "-i"])
    assert status == 130
    assert "aborted" in capsys.readouterr().err


def test_bad_share_dir_override_is_reported(tmp_path, monkeypatch, capsys):
    monkeypatch.setenv(pench.paths.SHARE_DIR_ENV, str(tmp_path / "absent"))
    assert pench.cli.run(["tex", "create"]) == 1
    assert "could not locate" in capsys.readouterr().err

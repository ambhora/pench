# --------------------------------------------------------------------------------------------------
# SPDX-License-Identifier: Apache-2.0
# Copyright (C) 2025 Jayesh Badwaik <jayesh@ambhora.com>
# --------------------------------------------------------------------------------------------------

import json
import os

import pytest

import pench.paths


def test_installed_layout_is_found(tmp_path):
    prefix = tmp_path / "prefix"
    (prefix / "bin").mkdir(parents=True)
    (prefix / "share" / "pench").mkdir(parents=True)
    (prefix / "bin" / "pench").write_text("")

    info = pench.paths.DirInfo(str(prefix / "bin" / "pench"))
    assert info.share_dir() == os.path.realpath(str(prefix / "share" / "pench"))


def test_environment_override_wins(tmp_path, monkeypatch):
    override = tmp_path / "elsewhere"
    override.mkdir()
    monkeypatch.setenv(pench.paths.SHARE_DIR_ENV, str(override))

    info = pench.paths.DirInfo(str(tmp_path / "bin" / "pench"))
    assert info.share_dir() == os.path.realpath(str(override))


def test_override_is_authoritative_not_a_fallback(tmp_path, monkeypatch):
    """A wrong override must fail loudly rather than silently using another tree."""
    monkeypatch.setenv(pench.paths.SHARE_DIR_ENV, str(tmp_path / "absent"))
    with pytest.raises(pench.paths.ShareDirNotFoundError):
        pench.paths.DirInfo(str(tmp_path / "bin" / "pench"))


def test_source_checkout_is_found(tmp_path, monkeypatch):
    monkeypatch.delenv(pench.paths.SHARE_DIR_ENV, raising=False)
    info = pench.paths.DirInfo(str(tmp_path / "nowhere" / "bin" / "pench"))
    assert os.path.isdir(info.doctype_template_dir())


def test_missing_share_dir_raises(tmp_path, monkeypatch):
    monkeypatch.setenv(pench.paths.SHARE_DIR_ENV, str(tmp_path / "absent"))
    with pytest.raises(pench.paths.ShareDirNotFoundError, match="could not locate"):
        pench.paths.DirInfo(str(tmp_path / "bin" / "pench"))


def test_derived_paths(dir_info):
    payload = json.loads(str(dir_info))
    assert payload["template_dir"].endswith(os.path.join("share", "pench", "template"))
    assert payload["texmf_dir"].endswith(os.path.join("share", "pench", "texmf"))
    assert dir_info.common_template_dir().endswith(os.path.join("template", "common"))

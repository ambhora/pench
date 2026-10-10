# --------------------------------------------------------------------------------------------------
# SPDX-License-Identifier: Apache-2.0
# Copyright (C) 2025 Jayesh Badwaik <jayesh@ambhora.com>
# --------------------------------------------------------------------------------------------------

"""Shared pytest fixtures."""

import os

import pytest

import pench.paths

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
SHARE_DIR = os.path.join(REPO_ROOT, "share", "pench")


@pytest.fixture
def dir_info(tmp_path):
    """A DirInfo pointed at the repository's share tree."""
    return pench.paths.DirInfo(str(tmp_path / "bin" / "pench"), share_dir=SHARE_DIR)


@pytest.fixture
def base_args(tmp_path):
    """A complete, valid argument dictionary for `pench tex create`."""
    return {
        "subcommand": "tex",
        "tex_subcommand": "create",
        "doctype": "article",
        "outdir": str(tmp_path / "out"),
        "title": "My Great Paper",
        "author": "Jane Doe",
        "email": "jane@example.com",
        "license": "CC-BY-4.0",
        "interactive": False,
        "parsable": False,
    }

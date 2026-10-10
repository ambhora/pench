# --------------------------------------------------------------------------------------------------
# SPDX-License-Identifier: Apache-2.0
# Copyright (C) 2025 Jayesh Badwaik <jayesh@ambhora.com>
# --------------------------------------------------------------------------------------------------

"""
Locating the data files that ship with pench.

The tool needs to find ``share/pench`` at runtime.  Where that lives depends on how pench was
invoked, so the lookup walks an ordered list of candidates instead of assuming one layout.
"""

import json
import os
import sys
import typing

#: Environment variable that overrides share directory discovery outright.
SHARE_DIR_ENV = "PENCH_SHARE_DIR"

#: Name of the directory, relative to a ``share`` root, that holds pench's data files.
SHARE_SUBDIR = os.path.join("share", "pench")


class ShareDirNotFoundError(RuntimeError):
    """Raised when pench cannot locate its installed data files."""


def _candidate_share_dirs(binary_dir: str) -> typing.List[str]:
    """
    Build the ordered list of directories that may contain pench's data files.

    :param binary_dir: Directory holding the running entry point script.
    :return: Candidate ``share/pench`` paths, most specific first.
    """
    override = os.environ.get(SHARE_DIR_ENV)
    if override:
        # An explicit override is authoritative: if it is wrong, say so rather than silently
        # falling back to a different tree and generating from templates nobody expected.
        return [override]

    candidates = []

    # Installed layout: <prefix>/bin/pench alongside <prefix>/share/pench.
    candidates.append(os.path.join(os.path.dirname(binary_dir), SHARE_SUBDIR))

    # Virtualenv / system interpreter prefixes, which is where hatch shared-data lands.
    candidates.append(os.path.join(sys.prefix, SHARE_SUBDIR))
    candidates.append(os.path.join(sys.base_prefix, SHARE_SUBDIR))

    # Source checkout: walk up from this file looking for the repository's share tree.
    here = os.path.dirname(os.path.realpath(__file__))
    while True:
        candidates.append(os.path.join(here, SHARE_SUBDIR))
        parent = os.path.dirname(here)
        if parent == here:
            break
        here = parent

    return candidates


def find_share_dir(binary_dir: str) -> str:
    """
    Return the first candidate share directory that actually exists.

    :param binary_dir: Directory holding the running entry point script.
    :raises ShareDirNotFoundError: If no candidate exists on disk.
    """
    candidates = _candidate_share_dirs(binary_dir)
    for candidate in candidates:
        if os.path.isdir(candidate):
            return os.path.realpath(candidate)

    searched = "\n  ".join(candidates)
    raise ShareDirNotFoundError(
        "could not locate the pench data directory.\n"
        f"Searched:\n  {searched}\n"
        f"Set {SHARE_DIR_ENV} to point at it explicitly."
    )


class DirInfo:
    """
    Resolved filesystem locations for a pench invocation.

    Exposes the entry point paths plus every data directory derived from them, so the rest of the
    code never has to join paths against ``share`` by hand.
    """

    def __init__(self, binary_path: str, share_dir: typing.Optional[str] = None):
        """
        :param binary_path: Path to the running entry point script.
        :param share_dir: Explicit share directory, bypassing discovery. Used by tests.
        :raises ShareDirNotFoundError: If discovery is needed and fails.
        """
        self._binary_path = os.path.realpath(binary_path)
        self._binary_dir = os.path.dirname(self._binary_path)
        self._root_dir = os.path.realpath(os.path.dirname(self._binary_dir))
        if share_dir is None:
            self._share_dir = find_share_dir(self._binary_dir)
        else:
            self._share_dir = os.path.realpath(share_dir)

    def binary_path(self) -> str:
        """Return the path to the entry point script."""
        return self._binary_path

    def binary_dir(self) -> str:
        """Return the directory holding the entry point script."""
        return self._binary_dir

    def root_dir(self) -> str:
        """Return the install prefix the entry point was launched from."""
        return self._root_dir

    def share_dir(self) -> str:
        """Return the ``share/pench`` directory holding all data files."""
        return self._share_dir

    def template_dir(self) -> str:
        """Return the root of the template tree."""
        return os.path.join(self._share_dir, "template")

    def common_template_dir(self) -> str:
        """Return the directory of files copied into every generated project."""
        return os.path.join(self.template_dir(), "common")

    def doctype_template_dir(self) -> str:
        """Return the directory holding one subdirectory per document type."""
        return os.path.join(self.template_dir(), "doctype")

    def texmf_dir(self) -> str:
        """Return the TDS-shaped texmf tree shipped with pench."""
        return os.path.join(self._share_dir, "texmf")

    def json(self) -> typing.Dict[str, str]:
        """Return a plain dictionary of every resolved path."""
        return {
            "binary_path": self._binary_path,
            "binary_dir": self._binary_dir,
            "root_dir": self._root_dir,
            "share_dir": self._share_dir,
            "template_dir": self.template_dir(),
            "common_template_dir": self.common_template_dir(),
            "doctype_template_dir": self.doctype_template_dir(),
            "texmf_dir": self.texmf_dir(),
        }

    def __repr__(self) -> str:
        return json.dumps(self.json(), indent=4)

    def __str__(self) -> str:
        return json.dumps(self.json(), indent=4)

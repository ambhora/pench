# --------------------------------------------------------------------------------------------------
# SPDX-License-Identifier: Apache-2.0
# Copyright (C) 2025 Jayesh Badwaik <jayesh@ambhora.com>
# --------------------------------------------------------------------------------------------------

"""TeX project scaffolding."""

import pench.tex.create
import pench.tex.license
import pench.tex.template
from pench.tex.create import UserInput, sanitize_title

# NOTE: `create` is deliberately not re-exported here. Binding the function to the name `create`
# would shadow the `pench.tex.create` submodule on this package, breaking `pench.tex.create.<name>`
# for every other importer. Callers go through `execute` instead.
from pench.tex.doctype import DocType
from pench.tex.template import TemplateRepository, TemplateError

__all__ = [
    "DocType",
    "TemplateError",
    "TemplateRepository",
    "UserInput",
    "execute",
    "sanitize_title",
]


def execute(dir_info, args):
    """
    Dispatch a parsed ``pench tex`` invocation to its subcommand.

    :param dir_info: Resolved :class:`pench.paths.DirInfo`.
    :param args: Parsed command line arguments as a dictionary.
    :raises ValueError: If the subcommand is not recognised.
    """
    subcommand = args.get("tex_subcommand")
    if subcommand == "create":
        return pench.tex.create.create(dir_info, args)

    raise ValueError(f"unknown tex subcommand: {subcommand}")

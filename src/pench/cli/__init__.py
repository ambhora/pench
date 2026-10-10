# --------------------------------------------------------------------------------------------------
# SPDX-License-Identifier: Apache-2.0
# Copyright (C) 2025 Jayesh Badwaik <jayesh@ambhora.com>
# --------------------------------------------------------------------------------------------------

"""Command line interface for the pench tool."""

import argparse
import os
import sys
import typing
import warnings

import pench.metadata
import pench.paths
import pench.tex
from pench.paths import DirInfo

__all__ = ["DirInfo", "main", "top_level_parser"]


def make_wide(formatter, w: int = 140, h: int = 100):
    """
    Return a wider help formatter where the private argparse API allows it.

    :param formatter: Formatter class to widen.
    :param w: Desired console width.
    :param h: Desired maximum help position.
    """
    try:
        # https://stackoverflow.com/a/5464440
        # beware: "Only the name of this class is considered a public API."
        kwargs = {"width": w, "max_help_position": h}
        formatter(None, **kwargs)
        return lambda prog: formatter(prog, **kwargs)
    except TypeError:
        warnings.warn("argparse help formatter failed, falling back.")
        return formatter


def build_tex_create_parser(parser: argparse.ArgumentParser,
                            doctypes: typing.Sequence[str]) -> None:
    """
    Add the options of ``pench tex create``.

    :param parser: Parser for the create subcommand.
    :param doctypes: Document types offered as choices, discovered from the template tree.
    """
    parser.add_argument("--doctype", choices=list(doctypes), help="type of document to create")
    parser.add_argument("--outdir", help="directory to create the project in")
    parser.add_argument("--title", help="document title")
    parser.add_argument("--subtitle", help="document subtitle")
    parser.add_argument("--subject", help="document subject")
    parser.add_argument("--author", help="author name")
    parser.add_argument("--email", help="author email address")
    parser.add_argument("--license", help="SPDX license identifier, e.g. CC-BY-4.0")
    parser.add_argument("--publishers", help="publisher shown on a Pench control page")
    parser.add_argument("--affiliation", help="IEEE author affiliation (organization)")
    parser.add_argument("--abstract", help="IEEE paper abstract; editable placeholder if omitted")
    parser.add_argument("--keywords", help="IEEE keywords (comma-separated)")
    parser.add_argument("--date", help="document date (default: today)")
    # Named --docversion, not --version, so it cannot be confused with the tool's own --version.
    parser.add_argument("--docversion", help="document version (default: 0.1)")
    parser.add_argument("--docid", help="document identifier (default: derived from author)")
    parser.add_argument(
        "--no-vendor-texmf",
        action="store_true",
        help="do not copy pench's texmf tree into the project",
    )
    parser.add_argument("-i", "--interactive", action="store_true",
                        help="prompt for anything not supplied on the command line")
    parser.add_argument("--parsable", action="store_true",
                        help="print only the created project path")


def build_texparser(texparser: argparse.ArgumentParser,
                    doctypes: typing.Sequence[str]) -> None:
    """
    Add the subcommands of ``pench tex``.

    :param texparser: Parser for the tex command.
    :param doctypes: Document types offered as choices.
    """
    subparser = texparser.add_subparsers(dest="tex_subcommand", required=True)
    create_parser = subparser.add_parser(
        "create",
        help="create a new tex project",
        formatter_class=make_wide(argparse.HelpFormatter),
    )
    build_tex_create_parser(create_parser, doctypes)


def top_level_parser(doctypes: typing.Optional[typing.Sequence[str]] = None
                     ) -> argparse.ArgumentParser:
    """
    Build the top-level pench parser.

    :param doctypes: Document types offered as choices. Defaults to the documented enum, used when
        the installed template tree could not be read.
    """
    if doctypes is None:
        doctypes = pench.tex.DocType.values()

    parser = argparse.ArgumentParser(description="pench : a tool for installing templates")
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {pench.metadata.__version__}",
        help="show the version of pench",
    )

    subparser = parser.add_subparsers(dest="subcommand", required=True)
    texparser = subparser.add_parser(
        "tex",
        help="install a tex template",
        formatter_class=make_wide(argparse.HelpFormatter),
    )
    build_texparser(texparser, doctypes)

    return parser


def run(argv: typing.Optional[typing.Sequence[str]] = None) -> int:
    """
    Execute pench and return a process exit status.

    :param argv: Argument vector excluding the program name. Defaults to ``sys.argv[1:]``.
    """
    if argv is None:
        argv = sys.argv[1:]

    binary_path = os.path.realpath(sys.argv[0]) if sys.argv and sys.argv[0] else __file__

    try:
        dir_info = pench.paths.DirInfo(binary_path)
    except pench.paths.ShareDirNotFoundError as error:
        print(f"pench: {error}", file=sys.stderr)
        return 1

    doctypes = pench.tex.TemplateRepository(dir_info).available()
    parser = top_level_parser(doctypes or None)
    args = parser.parse_args(argv)

    if args.subcommand != "tex":
        parser.error(f"unknown subcommand: {args.subcommand}")

    try:
        pench.tex.execute(dir_info, vars(args))
    except (ValueError, FileExistsError, OSError, pench.tex.TemplateError) as error:
        print(f"pench: {error}", file=sys.stderr)
        return 1
    except (KeyboardInterrupt, EOFError):
        print("\npench: aborted", file=sys.stderr)
        return 130

    return 0


def main() -> None:
    """Console script entry point."""
    sys.exit(run())

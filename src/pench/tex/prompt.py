# --------------------------------------------------------------------------------------------------
# SPDX-License-Identifier: Apache-2.0
# Copyright (C) 2025 Jayesh Badwaik <jayesh@ambhora.com>
# --------------------------------------------------------------------------------------------------

"""
Interactive prompting for missing metadata.

``readline`` is imported defensively: it is absent on Windows, and importing it unguarded at module
scope made the whole tool unimportable there even for fully non-interactive runs.
"""

import datetime
import typing

import pench.tex.create
import pench.tex.template
from pench.tex.doctype import DocType

try:
    import readline
except ImportError:  # pragma: no cover - platform dependent
    readline = None


def rlinput(prompt: str, prefill: str = "") -> str:
    """
    Prompt for a line of input, pre-filling the editable buffer where supported.

    :param prompt: Text shown to the user.
    :param prefill: Text placed in the input buffer for the user to edit.
    """
    if readline is None:
        suffix = f" [{prefill}]" if prefill else ""
        answer = input(f"{prompt}{suffix}").strip()
        return answer or prefill

    readline.set_startup_hook(lambda: readline.insert_text(prefill))
    try:
        return input(prompt)
    finally:
        readline.set_startup_hook()


def prompt_doctype(available: typing.Sequence[str]) -> str:
    """
    Ask the user to pick a document type from a numbered menu.

    Invalid entries re-prompt instead of raising, which the previous implementation did because it
    called ``int()`` on the raw input before its own validation could run.

    :param available: Installed document type names.
    :raises RuntimeError: If no document types are installed.
    """
    if not available:
        raise RuntimeError("no document templates are installed")

    while True:
        print("Select the index of the doctype:")
        for index, value in enumerate(available, start=1):
            print(f"{index}. {value}")

        answer = input("#? ").strip()
        try:
            selection = int(answer)
        except ValueError:
            print("Invalid input. Please enter an integer.\n")
            continue

        if not 1 <= selection <= len(available):
            print("Invalid input. Please enter a valid index.\n")
            continue

        return available[selection - 1]


def prompt_required(prompt: str, prefill: str = "") -> str:
    """
    Prompt until the user supplies a non-empty answer.

    :param prompt: Text shown to the user.
    :param prefill: Text placed in the input buffer for the user to edit.
    """
    while True:
        answer = rlinput(prompt, prefill).strip()
        if answer:
            return answer
        print("This field is required.\n")


def complete_user_input(dir_info, args: typing.MutableMapping[str, typing.Any]) -> typing.Dict:
    """
    Fill in every unset field by prompting, leaving supplied values untouched.

    :param dir_info: Resolved :class:`pench.paths.DirInfo`.
    :param args: Parsed command line arguments.
    """
    args = dict(args)
    repository = pench.tex.template.TemplateRepository(dir_info)

    if not args.get("doctype"):
        args["doctype"] = prompt_doctype(repository.available())
    elif isinstance(args["doctype"], DocType):
        args["doctype"] = args["doctype"].value

    if not args.get("title"):
        args["title"] = prompt_required("Title: ")

    if not args.get("outdir"):
        args["outdir"] = prompt_required("Output directory: ", ".")

    if not args.get("author"):
        args["author"] = prompt_required("Author: ", pench.tex.create.get_user_name())

    if not args.get("email"):
        args["email"] = prompt_required("Email: ", pench.tex.create.get_user_email())

    if not args.get("license"):
        args["license"] = prompt_required("License: ", "CC-BY-4.0")

    if args.get("subtitle") is None:
        args["subtitle"] = rlinput("Subtitle (optional): ").strip()

    if args.get("subject") is None:
        args["subject"] = rlinput("Subject (optional): ").strip()

    if args.get("publishers") is None and args["doctype"] != "ieee-conference":
        args["publishers"] = rlinput("Publisher (optional): ").strip()

    if args["doctype"] == "ieee-conference":
        if not args.get("affiliation"):
            args["affiliation"] = prompt_required("Affiliation: ", "Affiliation (edit before submission)")
        if not args.get("abstract"):
            args["abstract"] = prompt_required("Abstract: ", "Summarize the paper before submission.")
        if not args.get("keywords"):
            args["keywords"] = prompt_required("Keywords: ", "benchmarking, reproducibility")

    if not args.get("date"):
        args["date"] = prompt_required("Date: ", datetime.date.today().isoformat())

    if not args.get("docversion"):
        args["docversion"] = prompt_required("Document version: ", "0.1")

    if not args.get("docid"):
        default = pench.tex.create.default_docid(args["author"])
        args["docid"] = prompt_required("Document ID: ", default)

    return args

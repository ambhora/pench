# --------------------------------------------------------------------------------------------------
# SPDX-License-Identifier: Apache-2.0
# Copyright (C) 2025 Jayesh Badwaik <jayesh@ambhora.com>
# --------------------------------------------------------------------------------------------------

"""
SPDX license headers for generated files.

Every file pench writes gets a header in its own comment syntax.  Templates therefore ship without
one, which keeps the header format in a single place and stops generated files from ending up with
two stacked headers.
"""

import datetime
import os
import typing

#: Width of the rule drawn above and below a line-comment header.
RULE_WIDTH = 98

#: Comment style for each supported file type.
LINE_COMMENT_CHARS = {
    "tex": "%",
    "makefile": "#",
    "yaml": "#",
    "gitignore": "#",
    "perl": "#",
    "python": "#",
}

BLOCK_COMMENT_CHARS = {
    "markdown": ("<!--", "-->"),
}

#: Maps a generated file's name or extension onto a file type.
_FILETYPE_BY_NAME = {
    "makefile": "makefile",
    "gnumakefile": "makefile",
    ".latexmkrc": "perl",
    ".gitignore": "gitignore",
    ".gitlab-ci.yml": "yaml",
}

_FILETYPE_BY_EXTENSION = {
    ".tex": "tex",
    ".bib": "bibtex",
    ".sty": "tex",
    ".cls": "tex",
    ".yml": "yaml",
    ".yaml": "yaml",
    ".md": "markdown",
    ".py": "python",
    ".mk": "makefile",
}


class UnknownFileTypeError(ValueError):
    """Raised when no comment syntax is known for a file."""


def filetype_for(filename: str) -> str:
    """
    Infer a file type from a generated file's name.

    :param filename: Name the file will be written out as.
    :raises UnknownFileTypeError: If the name matches no known type.
    """
    basename = os.path.basename(filename)
    lowered = basename.lower()

    if lowered in _FILETYPE_BY_NAME:
        return _FILETYPE_BY_NAME[lowered]

    _, extension = os.path.splitext(lowered)
    if extension in _FILETYPE_BY_EXTENSION:
        return _FILETYPE_BY_EXTENSION[extension]

    known = ", ".join(sorted(set(_FILETYPE_BY_NAME) | set(_FILETYPE_BY_EXTENSION)))
    raise UnknownFileTypeError(f"no comment syntax known for '{basename}' (known: {known})")


def copyright_line(author: str, email: str, year: typing.Optional[int] = None) -> str:
    """
    Build the copyright statement placed in a header.

    :param author: Copyright holder.
    :param email: Contact address for the copyright holder.
    :param year: Copyright year; defaults to the current year.
    """
    if year is None:
        year = datetime.date.today().year
    return f"Copyright (C) {year} {author} <{email}>"


def line_header(license_id: str, author: str, email: str, comment_char: str) -> str:
    """
    Build a header using a line comment syntax, framed by rules.

    :param license_id: SPDX license identifier.
    :param author: Copyright holder.
    :param email: Contact address for the copyright holder.
    :param comment_char: Characters that begin a line comment.
    """
    rule = f"{comment_char} " + "-" * RULE_WIDTH
    return (
        f"{rule}\n"
        f"{comment_char} SPDX-License-Identifier: {license_id}\n"
        f"{comment_char} {copyright_line(author, email)}\n"
        f"{rule}\n"
    )


def block_header(
    license_id: str, author: str, email: str, comment_begin: str, comment_end: str
) -> str:
    """
    Build a header using a block comment syntax.

    :param license_id: SPDX license identifier.
    :param author: Copyright holder.
    :param email: Contact address for the copyright holder.
    :param comment_begin: Characters that open a block comment.
    :param comment_end: Characters that close a block comment.
    """
    return (
        f"{comment_begin}\n"
        f"- SPDX-License-Identifier: {license_id}\n"
        f"- {copyright_line(author, email)}\n"
        f"{comment_end}\n"
    )


def header(license_id: str, author: str, email: str, filetype: str) -> str:
    """
    Build a license header in the comment syntax of a given file type.

    :param license_id: SPDX license identifier.
    :param author: Copyright holder.
    :param email: Contact address for the copyright holder.
    :param filetype: File type as returned by :func:`filetype_for`.
    :raises UnknownFileTypeError: If the file type has no registered comment syntax.
    """
    if filetype == "bibtex":
        # BibTeX scans for @ even inside comments, so avoid email addresses.
        # Each @comment must be a single line; multi-line entries are fragile.
        return (f"@comment{{ SPDX-License-Identifier: {license_id} }}\n"
                f"@comment{{ Copyright (C) {datetime.date.today().year} {author} }}\n")

    if filetype in LINE_COMMENT_CHARS:
        return line_header(license_id, author, email, LINE_COMMENT_CHARS[filetype])

    if filetype in BLOCK_COMMENT_CHARS:
        comment_begin, comment_end = BLOCK_COMMENT_CHARS[filetype]
        return block_header(license_id, author, email, comment_begin, comment_end)

    known = ", ".join(sorted(set(LINE_COMMENT_CHARS) | set(BLOCK_COMMENT_CHARS)))
    raise UnknownFileTypeError(f"no comment syntax registered for file type '{filetype}' "
                               f"(known: {known})")


def header_for_file(license_id: str, author: str, email: str, filename: str) -> str:
    """
    Build a license header appropriate to a generated file's name.

    :param license_id: SPDX license identifier.
    :param author: Copyright holder.
    :param email: Contact address for the copyright holder.
    :param filename: Name the file will be written out as.
    :raises UnknownFileTypeError: If no comment syntax can be inferred.
    """
    return header(license_id, author, email, filetype_for(filename))

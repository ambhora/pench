# --------------------------------------------------------------------------------------------------
# SPDX-License-Identifier: Apache-2.0
# Copyright (C) 2025 Jayesh Badwaik <jayesh@ambhora.com>
# --------------------------------------------------------------------------------------------------

"""
Template discovery and rendering.

Templates are ordinary source files with ``@@placeholder@@`` markers.  That delimiter is used
instead of ``$name`` or ``{{ name }}`` because neither survives contact with TeX: ``$`` opens math
mode and braces are TeX's own grouping characters.  ``@@`` appears in no TeX construct, so a
template stays valid, compilable LaTeX even before it is rendered.
"""

import os
import re
import typing

#: Suffix marking a file as a template that must be rendered before it is written out.
TEMPLATE_SUFFIX = ".in"

#: Prefix standing in for a leading dot in a target filename.
DOTFILE_PREFIX = "dot-"

#: Filename a doctype directory must contain to count as an installed document type.
MAIN_TEMPLATE_NAME = "main.tex" + TEMPLATE_SUFFIX

_PLACEHOLDER_RE = re.compile(r"@@([a-z][a-z0-9_]*)@@")

_LATEX_ESCAPES = {
    "\\": r"\textbackslash{}",
    "&": r"\&",
    "%": r"\%",
    "$": r"\$",
    "#": r"\#",
    "_": r"\_",
    "{": r"\{",
    "}": r"\}",
    "~": r"\textasciitilde{}",
    "^": r"\textasciicircum{}",
}


class TemplateError(RuntimeError):
    """Raised when a template cannot be rendered or a document type is not installed."""


def latex_escape(text: str) -> str:
    """
    Escape the characters that TeX treats specially.

    Applied to user-supplied metadata before it is substituted into a ``.tex`` file, so a title
    containing ``R&D`` or ``100%`` does not break the build.

    :param text: Raw text supplied by the user.
    :return: Text safe to place in a TeX document body.
    """
    return "".join(_LATEX_ESCAPES.get(char, char) for char in text)


def placeholders(text: str) -> typing.Set[str]:
    """
    Return the set of placeholder names appearing in a template.

    :param text: Template contents.
    """
    return set(_PLACEHOLDER_RE.findall(text))


def render(text: str, context: typing.Mapping[str, str]) -> str:
    """
    Substitute every ``@@name@@`` placeholder using the supplied context.

    :param text: Template contents.
    :param context: Mapping of placeholder name to replacement text.
    :raises TemplateError: If the template uses a placeholder the context does not define.
    """
    missing = sorted(placeholders(text) - set(context))
    if missing:
        raise TemplateError("template uses undefined placeholder(s): " + ", ".join(missing))

    return _PLACEHOLDER_RE.sub(lambda match: context[match.group(1)], text)


def target_name(template_filename: str) -> str:
    """
    Map a template filename to the filename it is written out as.

    Strips the ``.in`` suffix and turns a leading ``dot-`` into a real leading dot.  Templates are
    stored undotted so that packaging tools, which routinely skip hidden files, do not silently
    drop them from the built wheel.

    :param template_filename: Basename of a file in the template tree.
    """
    name = template_filename
    if name.endswith(TEMPLATE_SUFFIX):
        name = name[: -len(TEMPLATE_SUFFIX)]
    if name.startswith(DOTFILE_PREFIX):
        name = "." + name[len(DOTFILE_PREFIX) :]
    return name


class TemplateRepository:
    """
    The installed template tree.

    Document types are discovered from the filesystem rather than hardcoded, so adding a new one is
    a matter of dropping a directory into ``share/pench/template/doctype`` with no code change.
    """

    def __init__(self, dir_info):
        """
        :param dir_info: Resolved :class:`pench.paths.DirInfo` for this invocation.
        """
        self._dir_info = dir_info

    def available(self) -> typing.List[str]:
        """Return the sorted names of every document type installed on disk."""
        root = self._dir_info.doctype_template_dir()
        if not os.path.isdir(root):
            return []

        found = []
        for entry in sorted(os.listdir(root)):
            if os.path.isfile(os.path.join(root, entry, MAIN_TEMPLATE_NAME)):
                found.append(entry)
        return found

    def has(self, doctype: str) -> bool:
        """
        Report whether a document type is installed.

        :param doctype: Document type name.
        """
        return doctype in self.available()

    def main_template(self, doctype: str) -> str:
        """
        Return the path to a document type's main TeX template.

        :param doctype: Document type name.
        :raises TemplateError: If that document type is not installed.
        """
        if not self.has(doctype):
            available = ", ".join(self.available()) or "none"
            raise TemplateError(
                f"no template installed for document type '{doctype}' "
                f"(available: {available})"
            )
        return os.path.join(self._dir_info.doctype_template_dir(), doctype, MAIN_TEMPLATE_NAME)

    @staticmethod
    def _template_files(root: str, *, omit_main: bool = False) -> typing.List[typing.Tuple[str, str]]:
        """Walk templates recursively; translate ``dot-`` in each path component."""
        files = []
        for directory, dirs, names in os.walk(root):
            dirs.sort()
            for name in sorted(names):
                source = os.path.join(directory, name)
                relative = os.path.relpath(source, root)
                if omit_main and relative == MAIN_TEMPLATE_NAME:
                    continue
                target = os.path.join(*(target_name(part) for part in relative.split(os.sep)))
                files.append((source, target))
        return files

    def doctype_files(self, doctype: str) -> typing.List[typing.Tuple[str, str]]:
        """Additional doctype files, including subdirectories, except main.tex.in.

        Document-type templates override common templates at matching paths.
        """
        self.main_template(doctype)  # Validate before creating the output directory.
        root = os.path.join(self._dir_info.doctype_template_dir(), doctype)
        return self._template_files(root, omit_main=True)

    def common_files(self) -> typing.List[typing.Tuple[str, str]]:
        """
        Return ``(source_path, target_name)`` for every file copied into all projects.

        :raises TemplateError: If the common template directory is missing.
        """
        root = self._dir_info.common_template_dir()
        if not os.path.isdir(root):
            raise TemplateError(f"common template directory is missing: {root}")

        return self._template_files(root)

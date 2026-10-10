# --------------------------------------------------------------------------------------------------
# SPDX-License-Identifier: Apache-2.0
# Copyright (C) 2025 Jayesh Badwaik <jayesh@ambhora.com>
# --------------------------------------------------------------------------------------------------

"""Document types pench knows how to scaffold."""

import pench.base


class DocType(pench.base.ExtendedEnum):
    """
    Types of TeX documents for Ambhora.

    Every member here must have a matching directory under ``share/pench/template/doctype`` and a
    matching class file in the texmf tree.  This enum is the documented set; what is actually
    offered at runtime comes from :class:`pench.tex.template.TemplateRepository`, which reads the
    installed template tree.  ``letter`` and ``beamer`` are deliberately absent until
    ``penchletter.cls`` and ``penchbeamer.cls`` exist -- listing them previously meant selecting
    either one failed partway through generation.
    """

    book = "book"
    article = "article"
    note = "note"
    ieee_conference = "ieee-conference"

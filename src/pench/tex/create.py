# --------------------------------------------------------------------------------------------------
# SPDX-License-Identifier: Apache-2.0
# Copyright (C) 2025 Jayesh Badwaik <jayesh@ambhora.com>
# --------------------------------------------------------------------------------------------------

"""
Generation of a new TeX project.

A generated project is self-contained: the rendered document, a makefile, a latexmk configuration
and -- unless suppressed -- a vendored copy of pench's texmf tree, so it builds anywhere with a
plain ``make``.
"""

import datetime
import json
import os
import re
import shutil
import subprocess
import typing
import unicodedata

import pench.tex.license
import pench.tex.template
from pench.tex.doctype import DocType

#: Metadata that must be present before generation can start.
REQUIRED_FIELDS = ("doctype", "outdir", "title", "author", "license", "email")

#: Characters with no ASCII decomposition that still have a conventional transliteration.
_TRANSLITERATIONS = {
    "ß": "ss",
    "æ": "ae",
    "Æ": "AE",
    "œ": "oe",
    "Œ": "OE",
    "ø": "o",
    "Ø": "O",
    "đ": "d",
    "Đ": "D",
    "ł": "l",
    "Ł": "L",
    "þ": "th",
    "Þ": "Th",
}


class UserInput:
    """Validated, fully populated metadata for one document."""

    def __init__(self, args: typing.Mapping[str, typing.Any]):
        """
        :param args: Parsed command line arguments, with every required field filled in.
        """
        self._outdir = args["outdir"]
        self._doctype = args["doctype"]
        self._title = args["title"]
        self._subtitle = args.get("subtitle") or ""
        self._subject = args.get("subject") or ""
        self._author = args["author"]
        self._license = args["license"]
        self._email = args["email"]
        self._publishers = args.get("publishers") or ""
        self._affiliation = args.get("affiliation") or "Affiliation (edit before submission)"
        self._abstract = args.get("abstract") or (
            "Summarize the problem, approach, principal results, and conclusions. "
            "Replace this text before submission."
        )
        self._keywords = args.get("keywords") or "benchmarking, reproducibility, performance evaluation"
        self._date = args.get("date") or datetime.date.today().isoformat()
        self._version = args.get("docversion") or "0.1"
        self._docid = args.get("docid") or default_docid(self._author)
        self._parsable = bool(args.get("parsable"))
        self._vendor_texmf = not bool(args.get("no_vendor_texmf"))

    def outdir(self) -> str:
        """Return the directory the project directory is created inside."""
        return self._outdir

    def doctype(self) -> DocType:
        """Return the document type."""
        return self._doctype

    def title(self) -> str:
        """Return the document title."""
        return self._title

    def subtitle(self) -> str:
        """Return the document subtitle."""
        return self._subtitle

    def subject(self) -> str:
        """Return the document subject."""
        return self._subject

    def author(self) -> str:
        """Return the author."""
        return self._author

    def license(self) -> str:
        """Return the SPDX license identifier."""
        return self._license

    def email(self) -> str:
        """Return the author's email address."""
        return self._email

    def publishers(self) -> str:
        """Return the publisher line."""
        return self._publishers

    def affiliation(self) -> str:
        """Return the affiliation line for IEEE documents."""
        return self._affiliation

    def abstract(self) -> str:
        """Return the abstract for IEEE documents."""
        return self._abstract

    def keywords(self) -> str:
        """Return comma-separated IEEE keywords."""
        return self._keywords

    def date(self) -> str:
        """Return the document date."""
        return self._date

    def version(self) -> str:
        """Return the document version."""
        return self._version

    def docid(self) -> str:
        """Return the document identifier printed on the control page."""
        return self._docid

    def parsable(self) -> bool:
        """Return whether output should be machine readable."""
        return self._parsable

    def vendor_texmf(self) -> bool:
        """Return whether pench's texmf tree is copied into the project."""
        return self._vendor_texmf

    def slug(self) -> str:
        """Return the sanitized title used for the directory and filenames."""
        return sanitize_title(self._title)

    def json(self) -> typing.Dict[str, typing.Any]:
        """Return a plain dictionary of every field."""
        return {
            "outdir": self._outdir,
            "doctype": self._doctype.value if self._doctype else None,
            "title": self._title,
            "subtitle": self._subtitle,
            "subject": self._subject,
            "author": self._author,
            "license": self._license,
            "email": self._email,
            "publishers": self._publishers,
            "affiliation": self._affiliation,
            "abstract": self._abstract,
            "keywords": self._keywords,
            "date": self._date,
            "version": self._version,
            "docid": self._docid,
            "parsable": self._parsable,
            "vendor_texmf": self._vendor_texmf,
            "slug": self.slug(),
        }

    def __repr__(self) -> str:
        return json.dumps(self.json())

    def __str__(self) -> str:
        return json.dumps(self.json(), indent=4)


def sanitize_title(title: str) -> str:
    """
    Reduce a title to a lowercase, hyphen-separated slug.

    Non-ASCII characters are transliterated rather than rejected, so a title such as
    ``Über Größe`` yields ``uber-groesse`` instead of raising.

    :param title: Raw title.
    :raises ValueError: If nothing usable survives sanitization.
    """
    transliterated = "".join(_TRANSLITERATIONS.get(char, char) for char in title)
    decomposed = unicodedata.normalize("NFKD", transliterated)
    ascii_title = decomposed.encode("ascii", "ignore").decode("ascii").strip()

    hyphenated = re.sub(r"[^0-9a-zA-Z-]+", "-", ascii_title.replace("'", ""))
    slug = re.sub(r"-+", "-", hyphenated).strip("-").lower()

    if not slug:
        raise ValueError(f"title '{title}' contains no characters usable in a filename")
    return slug


def default_docid(author: str, year: typing.Optional[int] = None) -> str:
    """
    Build a document identifier from the author's initials and the year.

    ``Jayesh Badwaik`` in 2025 yields ``JBAD-2025-0001``.

    :param author: Author name.
    :param year: Year to embed; defaults to the current year.
    """
    if year is None:
        year = datetime.date.today().year

    parts = [part for part in re.split(r"\s+", author.strip()) if part]
    ascii_parts = [
        unicodedata.normalize("NFKD", part).encode("ascii", "ignore").decode("ascii")
        for part in parts
    ]
    ascii_parts = [re.sub(r"[^A-Za-z]", "", part) for part in ascii_parts]
    ascii_parts = [part for part in ascii_parts if part]

    if not ascii_parts:
        prefix = "DOC"
    elif len(ascii_parts) == 1:
        prefix = ascii_parts[0][:4].upper()
    else:
        initials = "".join(part[0] for part in ascii_parts[:-1])
        prefix = (initials + ascii_parts[-1][:3]).upper()

    return f"{prefix}-{year}-0001"


def get_user_name() -> str:
    """Return the git-configured user name, or an empty string if git is unavailable."""
    return _git_config("user.name")


def get_user_email() -> str:
    """Return the git-configured user email, or an empty string if git is unavailable."""
    return _git_config("user.email")


def _git_config(key: str) -> str:
    """
    Read a value from git configuration.

    :param key: Configuration key to read.
    :return: The configured value, or an empty string when git is missing or the key is unset.
    """
    try:
        result = subprocess.run(
            ["git", "config", key],
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            check=False,
        )
    except (OSError, subprocess.SubprocessError):
        return ""
    return result.stdout.decode("utf-8", "replace").strip()


def build_context(user_input: UserInput) -> typing.Dict[str, str]:
    """
    Build the placeholder context for rendering a document type's TeX template.

    Free-text metadata is LaTeX-escaped; structural values such as the slug and the SPDX
    identifier are already restricted to safe characters and are passed through unchanged.

    :param user_input: Populated metadata.
    """
    escape = pench.tex.template.latex_escape
    return {
        "title": escape(user_input.title()),
        "subtitle": escape(user_input.subtitle()),
        "subject": escape(user_input.subject()),
        "author": escape(user_input.author()),
        "email": escape(user_input.email()),
        "publishers": escape(user_input.publishers()),
        "copyrightholder": escape(user_input.author()),
        "license": user_input.license(),
        "date": user_input.date(),
        "copyrightyear": str(datetime.date.today().year),
        "docid": user_input.docid(),
        "version": user_input.version(),
        "slug": user_input.slug(),
        "doctype": user_input.doctype().value,
        # IEEE requires its own publisher-prescribed class and pdfLaTeX/BibTeX.
        # Existing Pench documents use LuaLaTeX and biblatex/biber.
        "latexmk_engine": "-pdf" if user_input.doctype() == DocType.ieee_conference else "-lualatex",
        "affiliation": escape(user_input.affiliation()),
        "abstract": escape(user_input.abstract()),
        "keywords": escape(user_input.keywords()),
    }


def write_rendered(source: str, target: str, context: typing.Mapping[str, str], license_id: str,
                   author: str, email: str) -> None:
    """
    Render one template and write it out with a license header on top.

    :param source: Path to the template file.
    :param target: Path the rendered file is written to.
    :param context: Placeholder context.
    :param license_id: SPDX license identifier for the header.
    :param author: Copyright holder for the header.
    :param email: Contact address for the header.
    """
    with open(source, "r", encoding="utf-8") as handle:
        body = handle.read()

    rendered = pench.tex.template.render(body, context)
    header = pench.tex.license.header_for_file(license_id, author, email, os.path.basename(target))

    with open(target, "w", encoding="utf-8") as handle:
        handle.write(header)
        handle.write(rendered)


def create_implementation(dir_info, user_input: UserInput) -> str:
    """
    Generate the project directory and everything inside it.

    The directory is removed again if any step fails, so a failed run never leaves a half-built
    project behind.

    :param dir_info: Resolved :class:`pench.paths.DirInfo`.
    :param user_input: Populated metadata.
    :raises FileExistsError: If the target directory already exists.
    :return: Absolute path of the generated project directory.
    """
    repository = pench.tex.template.TemplateRepository(dir_info)
    doctype = user_input.doctype().value

    # Fail before creating anything if the document type is not installed.
    main_template = repository.main_template(doctype)
    common_files = repository.common_files()
    doctype_files = repository.doctype_files(doctype)

    slug = user_input.slug()
    projectdir = os.path.join(os.path.abspath(user_input.outdir()), slug)

    if os.path.exists(projectdir):
        raise FileExistsError(f"directory {projectdir} already exists")

    if not user_input.parsable():
        print(f"Creating a {doctype} document in {projectdir} ...")

    context = build_context(user_input)
    license_id = user_input.license()
    author = user_input.author()
    email = user_input.email()

    os.makedirs(projectdir)
    try:
        write_rendered(main_template, os.path.join(projectdir, f"{slug}.tex"), context,
                       license_id, author, email)

        # Document-specific templates may override a common file, e.g. an IEEE makefile.
        # Other doctype assets (such as references.bib) are rendered in the same pass.
        files = dict((target, source) for source, target in common_files)
        files.update((target, source) for source, target in doctype_files)
        for target, source in sorted(files.items()):
            if target == f"{slug}.tex" or target == "main.tex":
                raise pench.tex.template.TemplateError(
                    f"document type '{doctype}' uses a reserved filename: {target}"
                )
            destination = os.path.join(projectdir, target)
            os.makedirs(os.path.dirname(destination), exist_ok=True)
            write_rendered(source, destination, context, license_id, author, email)

        if user_input.vendor_texmf():
            shutil.copytree(dir_info.texmf_dir(), os.path.join(projectdir, "texmf"))
    except Exception:
        shutil.rmtree(projectdir, ignore_errors=True)
        raise

    if user_input.parsable():
        print(projectdir)
    else:
        print(f"Created {os.path.join(projectdir, slug)}.tex")
        print(f"Build it with: cd {projectdir} && make")

    return projectdir


def missing_fields(args: typing.Mapping[str, typing.Any]) -> typing.List[str]:
    """
    Return the names of required fields that are still unset.

    :param args: Parsed command line arguments.
    """
    return [field for field in REQUIRED_FIELDS if not args.get(field)]


def create(dir_info, args: typing.MutableMapping[str, typing.Any]) -> str:
    """
    Entry point for ``pench tex create``.

    :param dir_info: Resolved :class:`pench.paths.DirInfo`.
    :param args: Parsed command line arguments.
    :raises ValueError: If fields are missing and interactive mode was not requested.
    :return: Absolute path of the generated project directory.
    """
    if args.get("interactive"):
        import pench.tex.prompt

        args = pench.tex.prompt.complete_user_input(dir_info, args)
    else:
        missing = missing_fields(args)
        if missing:
            raise ValueError(
                "missing required option(s): " + ", ".join(f"--{name}" for name in missing)
                + "\nSupply them, or pass --interactive to be prompted."
            )

    if not isinstance(args["doctype"], DocType):
        args["doctype"] = DocType.from_value(args["doctype"])

    return create_implementation(dir_info, UserInput(args))

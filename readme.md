<!--
- SPDX-License-Identifier: Apache-2.0
- Copyright (C) 2025 Jayesh Badwaik <jayesh@ambhora.com>
-->

# pench - A Scaffolding Tool for Ambhora Projects

`pench` generates a complete, self-contained LaTeX project from a document type and some metadata.
The generated directory carries its own copy of the Ambhora class files, so it builds anywhere with
a plain `make`.

## Usage

```sh
pench tex create \
  --doctype article \
  --title "Notes on Diffusion" \
  --author "Jayesh Badwaik" \
  --email jayesh@ambhora.com \
  --license CC-BY-4.0 \
  --outdir .
```

Anything omitted can be filled in by prompt with `-i`/`--interactive`, which prefills the author and
email from `git config`. `--parsable` prints only the created path, so it composes:

```sh
cd "$(pench tex create --parsable ...)" && make
```

Optional metadata: `--subtitle`, `--subject`, `--publishers`, `--date`, `--docversion`, `--docid`.
Pass `--no-vendor-texmf` to skip copying the class files into the project, for repositories that
rely on a system-wide installation instead.

## IEEE conference papers

The IEEE conference variant uses the original IEEEtran class rather than a Pench
article class. It produces an IEEE-compatible two-column conference source with
numerical citations, a BibTeX bibliography, author blocks, a compact editable
sample, and a README explaining submission-specific changes.

```sh
pench tex create \
  --doctype ieee-conference \
  --title "Portable Performance Benchmarks" \
  --author "Jane Doe" \
  --email "jane@example.org" \
  --affiliation "Example Research Centre" \
  --keywords "HPC, benchmarking, reproducibility" \
  --license CC-BY-4.0 \
  --outdir .

cd portable-performance-benchmarks
make
```

`--abstract` is optional; otherwise the generated source includes placeholder text.
IEEE class and BibTeX sources are copied unmodified from the supplied IEEE
archives; their original LPPL notices are retained. The project license applies
to newly generated files, **not** to the vendored IEEEtran implementation.
Check the final venue's requirements, including copyright and submission policy.

Build engines are chosen per document type: IEEE uses pdfLaTeX/BibTeX, whereas
Pench article/book/note use LuaLaTeX with biblatex/Biber when needed. The make
command does not enable `-shell-escape` by default. The `.latexmkrc` uses an
absolute project-local texmf path so that BibTeX still finds the provided
styles when running in the build directory.

## Generated project

```
my-title/
├── my-title.tex        # rendered from the doctype template, with your metadata substituted in
├── makefile            # `make` to build, `make verbose` for the full log, `make clean`
├── texmf/              # vendored Pench classes, assets, and IEEEtran sources
├── .latexmkrc          # points TeX and BibTeX at the project texmf tree
├── .gitignore
├── .gitlab-ci.yml
└── .github/workflows/build.yml  # GitHub Actions PDF build
```

## Repository layout

```
src/pench/
├── base/           # ExtendedEnum and other shared primitives
├── paths.py        # locating share/pench at runtime
├── cli/            # argument parsing and process exit status
└── tex/
    ├── doctype.py  # the document types that have class files
    ├── template.py # template discovery and @@placeholder@@ rendering
    ├── license.py  # SPDX headers per comment syntax
    ├── prompt.py   # interactive input
    └── create.py   # project generation

share/pench/
├── template/
│   ├── common/     # files copied into every project
│   └── doctype/    # one directory per document type
└── texmf/          # TDS-shaped tree: texmf/tex/latex/pench/
```

See [CONSOLIDATION.md](CONSOLIDATION.md) for detailed source comparisons and
integration decisions, and [docs/ieee](docs/ieee) for the original IEEE
reference instructions.

Everything pench installs lives under `share/pench`. The previous layout put the class files in
`share/tex/texmf`, which collides with the TeX Directory Structure convention that TeX Live itself
uses for `$prefix/share/texmf`; installing into a shared prefix would have mixed pench's files into
that tree.

## Templates

Templates are ordinary source files containing `@@placeholder@@` markers. That delimiter is used in
preference to `$name` or `{{ name }}` because `$` opens math mode in TeX and braces are TeX's own
grouping characters, so a template remains valid, compilable LaTeX before it is rendered.

Available placeholders: `title`, `subtitle`, `subject`, `author`, `email`, `publishers`,
`affiliation`, `abstract`, `keywords`, `copyrightholder`, `license`, `date`,
`copyrightyear`, `docid`, `version`, `slug`, `doctype`, `latexmk_engine`.

Free-text values are LaTeX-escaped on substitution, so a title such as `R&D at 100%` does not break
the build.

Files in `template/common/` follow two naming conventions: the `.in` suffix is stripped on output,
and a leading `dot-` becomes a real leading dot. Subdirectories are supported, so
`common/dot-github/workflows/build.yml.in` generates `.github/workflows/build.yml`. Templates are therefore stored undotted, because
packaging tools routinely skip hidden files and would otherwise drop them from the built wheel.

License headers are **not** stored in the templates. Every generated file gets one prepended in its
own comment syntax, which keeps the format in one place and stops files from acquiring two stacked
headers.

## Adding a document type

Document types are discovered from the filesystem, so no code change is needed to install one:

1. Add `share/pench/texmf/tex/latex/pench/penchTYPE.cls`.
2. Add `share/pench/template/doctype/TYPE/main.tex.in`.
3. Add the member to `DocType` in `src/pench/tex/doctype.py` to document it.

Any additional plain files placed in `template/doctype/TYPE/` (for example
`references.bib.in` or `README.md.in`) are generated alongside the main source.
Document-type files may override files with the same output name from `common/`.


`letter` and `beamer` are currently absent because `penchletter.cls` and `penchbeamer.cls` do not
exist yet. They were previously offered as choices, which meant selecting either one failed partway
through generation, after the output directory had already been created.

## Development

```sh
uv run --group dev pytest
uv build
```

The repository's [GitHub Actions CI](.github/workflows/ci.yml) checks Python 3.9/3.12/3.13,
builds and installs a wheel to verify packaged shared data, and compiles all four LaTeX document
types. The latter requires a complete TeX Live environment and takes longer than Python tests.
Every generated project includes a separate `.github/workflows/build.yml` which builds its PDF
and uploads it as a workflow artifact. Both workflows use read-only GitHub permissions.
GitLab CI remains available alongside GitHub Actions.

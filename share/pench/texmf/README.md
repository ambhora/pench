# Vendored TeX assets

The `tex/latex/pench` sources are from the Pench archives and retain their
original licensing notices. The `penchassets/` tree (PDF logos and SPDX
license-name helpers) is restored from `package-2.tar.gz`, which contains
assets missing from the later `package.tar` archive. The `penchdesign.sty`
font selection has been updated to provide portable fallback fonts when the
original design fonts are unavailable. The IEEE files below are byte-for-byte copies
from the two supplied IEEE archives, each with its own original LPPL notices:

- `tex/latex/ieeetran/IEEEtran.cls` — version 1.8b (2015-08-26), provided in
  `conference-latex-template(1).zip` (IEEE conference template dated 2024).
- `bibtex/bst/ieeetran/IEEEtran.bst` and `IEEEtranS.bst` — version 1.12
  (2007-01-11), provided in `IEEEtranBST2.zip`.
- `bibtex/bib/ieeetran/IEEEabrv.bib` — journal-name abbreviations from the
  same bibliography archive.

Only the generated document files receive the user's chosen license header.
Third-party IEEE sources are **never** rewritten or given a Pench license
header. See upstream code for the LPPL notices and authorship credits.

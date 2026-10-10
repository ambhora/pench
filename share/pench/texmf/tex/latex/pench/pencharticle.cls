% ------------------------------------------------------------------------------
% SPDX-License-Identifier: CC-BY-4.0
% Copyright (C) 2024 Jayesh Badwaik <j.badwaik@fz-juelich.de>
% ------------------------------------------------------------------------------
\NeedsTeXFormat{LaTeX2e}
\ProvidesClass{pencharticle}
\LoadClassWithOptions{scrartcl}

\RequirePackage{penchcommon}
\RequirePackage{penchmath}

% --------------------------------------------------------------------------------------------------
% Configure ToC Tools
% --------------------------------------------------------------------------------------------------
\PassOptionsToClass{headings=optiontoheadandtoc}{scrartcl}
\setcounter{secnumdepth}{3}
\setcounter{tocdepth}{2}

\RedeclareSectionCommand[tocbeforeskip=1.0ex,tocnumwidth=2.0em]{part}
\RedeclareSectionCommand[tocbeforeskip=0.5ex,tocindent=1.0em,tocnumwidth=2.0em]{section}
\RedeclareSectionCommand[tocbeforeskip=0.0ex,tocindent=2.5em,tocnumwidth=2.5em]{subsection}

% --------------------------------------------------------------------------------------------------
% Configure Headers
% --------------------------------------------------------------------------------------------------
\RequirePackage[automark,autooneside=false]{scrlayer-scrpage}
\RequirePackage{xparse}
\RequirePackage{etoolbox}
\addtokomafont{pageheadfoot}{\small}
\RequirePackage{ifoddpage}


\defpairofpagestyles{title}{
  \clearpairofpagestyles
  \cfoot{\rule[\baselineskip]{\textwidth}{0.1pt}}
  \ofoot{\pagemark}
}
\renewcommand*{\titlepagestyle}{title}

\automark[subsection]{section}

\if@twoside

  \defpairofpagestyles{main}{
    \clearpairofpagestyles
    \cfoot{\rule[\baselineskip]{\textwidth}{0.1pt}}
    \chead{\rule[-\baselineskip]{\textwidth}{0.1pt}}
    \ofoot{\pagemark}
    \lehead{\leftmark}
    \rohead{\Ifstr{\rightmark}{}{\leftmark}{\rightmark}}
  }

\else
  \defpairofpagestyles{main}{
    \clearpairofpagestyles
    \cfoot{\rule[\baselineskip]{\textwidth}{0.1pt}}
    \chead{\rule[-\baselineskip]{\textwidth}{0.1pt}}
    \ofoot{\pagemark}
    \ohead{\rightmark}
  }
\fi


% --------------------------------------------------------------------------------------------------
% Configure Part Titles to be on a Separate Page
% --------------------------------------------------------------------------------------------------
\renewcommand\partheadstartvskip{\clearpage\null\vfil}
\renewcommand\partheadmidvskip{\par\nobreak\vskip 20pt\thispagestyle{empty}}
\renewcommand\partheadendvskip{\vfil\clearpage}
\renewcommand\raggedpart{\centering}

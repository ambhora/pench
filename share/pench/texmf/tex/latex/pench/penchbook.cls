% --------------------------------------------------------------------------------------------------
% SPDX-License-Identifier: Apache-2.0
% Copyright (C) 2025 Jayesh Badwaik <jayesh@ambhora.com>
% --------------------------------------------------------------------------------------------------
\NeedsTeXFormat{LaTeX2e}
\ProvidesClass{penchbook}
\LoadClassWithOptions{scrbook}

\RequirePackage{penchcommon}
\RequirePackage{penchmath}

% --------------------------------------------------------------------------------------------------
% Configure ToC Tools
% --------------------------------------------------------------------------------------------------
\RequirePackage{tocbibind}
\PassOptionsToClass{headings=optiontoheadandtoc}{scrbook}
\setcounter{secnumdepth}{3}
\setcounter{tocdepth}{2}

\RedeclareSectionCommand[tocnumwidth=2.0em]{part}
\RedeclareSectionCommand[tocindent=1em,tocnumwidth=2.0em]{chapter}
\RedeclareSectionCommand[tocindent=2.5em,tocnumwidth=2.0em]{section}
\RedeclareSectionCommand[tocindent=4.0em,tocnumwidth=3.0em]{subsection}


% --------------------------------------------------------------------------------------------------
% Configure Headers
% --------------------------------------------------------------------------------------------------
\RequirePackage[automark,autooneside=false]{scrlayer-scrpage}
\RequirePackage{xparse}
\RequirePackage{etoolbox}
\addtokomafont{pageheadfoot}{\small}
\RequirePackage{ifoddpage}

\defpairofpagestyles{chapter}{
  \clearpairofpagestyles
  \cfoot{\rule[\baselineskip]{\textwidth}{0.1pt}}
  \ofoot{\pagemark}
}
\renewcommand*{\chapterpagestyle}{chapter}

\automark[section]{chapter}

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
% Configure Chapter title
% --------------------------------------------------------------------------------------------------
% Set Font Size of Chapter Title Text
\addtokomafont{chapter}{
  \fontsize{1.8ex}{1.8ex}\selectfont
}

% Set Font Size of Chapter Number Text
\newkomafont{chapternumber}{
  \fontsize{5ex}{5ex}\selectfont
}

% Set Font Size of Chapter Name Text
\newkomafont{chaptername}{
  \itshape\rmfamily\normalsize
}

\renewcommand{\chapterlinesformat}[3]{%
  \begin{minipage}[t][][t]{0.20\textwidth}
    \begin{center}
      #2
    \end{center}
  \end{minipage}
  ~
  \begin{minipage}[t][][t]{0.79\textwidth}
    \begin{minipage}[t][][t]{0.99\textwidth}
    \linespread{1.5}\selectfont
    \begin{flushleft}
      #3
    \end{flushleft}
    \end{minipage}
  \end{minipage}
}

% Set Chapter Formatting
\renewcommand\chapterformat{
  \begin{minipage}[t][][t]{0.60\textwidth}
  \begin{center}
    \usekomafont{chaptername}{\chaptername}\\
    \usekomafont{chapternumber}{\thechapter}
  \end{center}
  \end{minipage}
  \begin{minipage}[t][][t]{0.30\textwidth}
  \begin{center}
    \rule[-6ex]{1pt}{8ex}\enskip\enskip\enskip
  \end{center}
  \end{minipage}
}

\RedeclareSectionCommand[
  beforeskip=0pt,   % Space before the chapter title
  afterskip=4\baselineskip,   % Space after the chapter title
]{chapter}

% --------------------------------------------------------------------------------------------------
% Indexing
% --------------------------------------------------------------------------------------------------

\RequirePackage[acronym,symbols,nogroupskip]{glossaries-extra}
\setabbreviationstyle[acronym]{long-short}

% ------------------------------------------------------------------------------
% SPDX-License-Identifier: CC-BY-4.0
% Copyright (C) 2024 Jayesh Badwaik <j.badwaik@fz-juelich.de>
% ------------------------------------------------------------------------------
\NeedsTeXFormat{LaTeX2e}
\ProvidesClass{penchnote}
\LoadClassWithOptions{scrartcl}

\RequirePackage{penchcommon}

% --------------------------------------------------------------------------------------------------
% Configure Title
% --------------------------------------------------------------------------------------------------
\renewcommand{\maketitle}{
\begin{center}
\noindent
\begin{minipage}{0.49\textwidth}
    \begin{flushleft}
    \textbf{Author:} \@author
    \end{flushleft}
\end{minipage}
\hfill
\begin{minipage}{0.49\textwidth}
    \begin{flushright}
      \textbf{Date:} \@date
    \end{flushright}
\end{minipage}

\begin{Large}
\sffamily \bfseries \@title \par
\end{Large}
\vspace{2ex}
\rule{\textwidth}{0.1pt}
\end{center}
}

\renewcommand{\section}[1]
{
  \PackageError{penchnote}
  {\noexpand\section is disabled}
  {If you want to use sections, please use the \texttt{pencharticle} class instead.}
}

\renewcommand{\subsection}[1]
{
  \PackageError{penchnote}
  {\noexpand\subsection is disabled}
  {If you want to use subsections, please use the \texttt{pencharticle} class instead.}
}

\renewcommand{\subsubsection}[1]
{
  \PackageError{penchnote}
  {\noexpand\subsubsection is disabled}
  {If you want to use subsubsections, please use the \texttt{pencharticle} class instead.}
}

\renewcommand{\part}[1]
{
  \PackageError{penchnote}
  {\noexpand\part is disabled}
  {If you want to use parts, please use the \texttt{pencharticle} class instead.}
}

% --------------------------------------------------------------------------------------------------
% Configure ToC Tools
% --------------------------------------------------------------------------------------------------
\PassOptionsToClass{headings=optiontoheadandtoc}{scrartcl}
\setcounter{secnumdepth}{3}

% --------------------------------------------------------------------------------------------------
% Configure Headers
% --------------------------------------------------------------------------------------------------
\RequirePackage[automark,autooneside=false]{scrlayer-scrpage}
\defpairofpagestyles{title}{
  \clearpairofpagestyles
  \cfoot{\rule[\baselineskip]{\textwidth}{0.1pt}}
  \ofoot{\pagemark}
}

\defpairofpagestyles{main}{
  \clearpairofpagestyles
  \cfoot{\rule[\baselineskip]{\textwidth}{0.1pt}}
  \automark[subsection]{section}
  \ofoot{\pagemark}
}

\renewcommand*{\titlepagestyle}{title}

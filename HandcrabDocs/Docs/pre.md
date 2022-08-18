![](../CEMC_header.png)

# [Handcrab Documentation &mdash; Preprocessing](index.html)

## Introduction

Handcrab can process and filter through certain elements of the LaTeX file(s) before cmpiling to HTML. These processes run for every file specified either with the `--input` or `-i` argument, or with appended LaTeX files called by `\input{}`.

Handcrab takes care of three major things before conversion:

- Removal of unwated LaTeX tags
- Repositioning of [Handcrab environments](env.html)
- Application of LaTeX skeletons (specified by `--skeleton` or `-s`)

## Removal of Unwanted LaTeX Commands

The following commands are removed by Handcrab, and only the important contents will remain.

- raisebox
- fbox
- phantom (on request, using `-p`)
- graphicspath
- comments
- tikz graphics (on request, using `-dt`)
- minipages (can be kept on request, using `-m`)
- vspace & hspace
- flush environments (on request, using `-rf`)
- framebox
- parbox

## Lists

The usage of `[label=(\aleph*)]` and `[label=(\Aleph*)]` from `\begin{enumerate}` and `\begin{itemize}` is removed and replaced with `[a]` and `[A]` respectively.

List environments should work as intended with latex.
For example, `\begin{enumerate}[A.]` and `\begin{itemize}[A.]`
will have the same effect in the HTML, and `\item[...]` will also
be preserved, regardless of if the list was enumerate or itemize.

Nested enumeration does not change types by default, so in the following example code,

```.{multiline}
\begin{enumerate}
\item text one
\item text two
	\begin{enumerate}
		\item text two point five
		\itme text two point seven five
	\end{enumerate}
\item text three
\end{enumerate}
```

LaTeX would naturally make the second enumerate use letters instead of numbers. This
will not be preserved. The nested enumeration will come out as numbered. However, if
the nested enumeration started with `\begin{enumerate}[A.]`, then it will come out
using letters.

This feature was required to get contest files working.

For contests with custom list structures, such as BCC, Gauss and PCF,
the output will respect those list structures as long as the template is specified.

For example, compiling BCC without using `-t bcc` will not
create the special multiple choice lists.

 
## Repositioning of Handcrab Environments

This section doesn't really need much explaining, aside from the
fact that it allows for the user to be lenient with how they place
the handcrab environment tags.

## Application of LaTeX skeletons

If a skeleton file ending in `.tex` is given using the `--skeleton` or `-s` argument, then this skeleton will be applied to the input file before conversion. The skeleton file must only contain the preamble and the following code:

```{.multiline}
\begin{document}
%!CONTENT!%
\end{document}
```

`%!CONTENT!%` will be replaced with everything between `\begin{document}` and `\end{document}` of the input files. This ensures that any newcommands or new environments can be overwritten if necessary.

It should be noted that both an HTML and LaTeX template can be provided using `--skeleton` or `-s` in any order.

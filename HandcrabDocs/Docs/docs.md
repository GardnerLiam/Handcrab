![](../CEMC_header.png)

# Handcrab Documentation

## Introduction

Handcrab is a wrapper around pandoc that automates some of the HTML
formatting. Currently, handcrab can automate the styling of row headers
and row/column headers in tables (column headers are done in pandoc by
default), and can fill in the alt text for images. It can also create
the description box with the hide/reveal button in case the alt tag
isn’t big enough to hold the description. Handcrab comes with the
`--help` or `-h` tags in order to view the passable arguments. Those
arguments are as follows:

| **Argument Name**            | **Short-Form** | **Description**                             |
|------------------------------|----------------|---------------------------------------------|
| `--input`                    | `-i`           | Input TeX file(s)                           |
| `--output`                   | `-o`           | Output HTML file                            |
| `--skeleton`                 | `-s`           | Skeleton file for formatting HTML output    |
| `--template`                 | `-t`           | Compiling instruction common CEMC resources |
| `--heading-level`            | `-hl`          | Shifts highest heading level down in output |
| `--remove-phantom`           | `-p`           | Removes `\phantom{}` tags from the output   |
| `--keep-minipages`           | `-m`           | Does not remove minipages in output         |
| `--image-folder`             | `-if`          | Specifies directory for images              |
| `--css`                      | `-css`         | Overrides path to CSS stylesheet            |
| `--title`                    | `-n`           | Overrides the HTML `<title>` tag            |
| `--disable-tikz`             | `-dt`          | Removes all tikz instances from file        | 
| `--tikz-pdf`                 | `-tp`          | Tikz graphics will render as cropped PDFs   | 
| `--remove-flush`             | `-rf`          | Removes flushleft/flushright environments   |
| `--verbose`                  | `-V`           | Displays any log messages                   |
| `--help`                     | `-h`           | Displays help message                       |
| `--keep-markers`             | `-k`           | Any markers left from bugs will remain      |
| `--disable-helper-functions` | `-dhf`         | Disables template-specific modifications    |

For example, if your input file was `Folder/MyInput.tex` and you wanted
to write the HTML `Folder2/MyOutput.html` you could run the following
command:

```
handcrab -i "Folder/MyInput.tex" -o "Folder2/MyOutput.html"
```

It should be noted that the `--output` or `-o` option may be left blank, and in such instances the name of the original file will be used for the output name. For example,

```
handcrab -i "Folder/MyInput.tex"
```

will output a the file `Folder/MyInput.html`. 

### Outputting to directories

It should also be noted that if the output is a directory instead of a file, it will output the file into that directory. For example:

```
handcrab -i "myFile.tex" -o "myDirectory/"
```

will output the file `myDirectory/myFile.html`.

All references to other resources, such as image folders and css are relative to the directory the command is run in. For example, in the command

```
handcrab -i "myFile.tex" -if "../myImages" -o "myDirectory"
```

All image outputs will have their source directory be `../myImages` and **not** `../../myImages`.

### Skeletons

A skeleton HTML or TeX file can be provided using the `-s` or `--skeleton` argument. If given an HTML file, Handcrab will replace `<p>Content</p>` with the body of the output. If given a TeX file, handcrab will replace `%!CONTENT!%` with the body of the TeX file before compiling. 

```
handcrab -i "Folder/MyInput.tex" -o "Folder2/MyOutput.html" -s sktn.html
```

Handcrab has some default skeleton files as well, which can be accessed by passing in their *abbreviation*, a table of which can be seen below.


| **Filename**                | **Abbreviation** | **Purpose**                                        |
|-----------------------------|------------------|----------------------------------------------------|
|`CCCProblemTemplate.html`    | `cccProblem`     | For compiling a single CCC problem                 |
|`CCCSkeletonFull.html`       | `cccFull`        | For compiling multiple CCC questions into one file |
|`BCCSkeleton.tex`            | `bccTeX`         | Removes Tikz from the BCC rendering commands       |
|`BCCSkeleton.html`           | `bccFull`        | For compiling BCC contests                         |
|`POTM.html`                  | `potm`           | For compiling POTM questions                       |
|`POTW.html`                  | `potw`           | For compiling POTW questions                       |
|`MathCirclesLesson.html`     | `mcLesson`       | For compiling Math Circles lesson files            |
|`MathCirclesProblemSet.html` | `mcProbset`      | For compiling Math Circles problem set files       |
|`MathCirclesSolution.html`   | `mcSoln`         | For compiling Math Circles solution files          |
|`CTMC.html`                  | `ctmc`           | For compiling all CTMC resources                   |
|`GaussContest.tex`           | `gaussTeX`       | For compiling Gauss contest files                  |
|`GaussContest.html`          | `gaussContest`   | For compiling Gauss contest files                  |
|`GaussPCFSolution.tex`       | `gaussSolnTeX`   | For compiling Gauss solution files                 |
|`GaussPCFSolution.tex`       | `pcfSolnTeX`     | For compiling PCF solution files                   |
|`PCFContest.html`            | `pcfContest`     | For compiling PCF contest files                    |
|`EuclidContest.tex`          | `euclidTeX`      | For compiling Euclid contest files                 |
|`EuclidContest.html`         | `euclidContest`  | For compiling Euclid contest files                 |
|`rendertikz.tex`             | `tikz`           | For compiling standalone tikz graphics             |

Two skeleton files can be provided together if one is an HTML file and the other is a LaTeX file. This is the only instance in which multiple files may be provided using the `--skeleton` or `-s` argument. 

It should be noted that when using any [templates](#templates), the skeleton will automatically
be chosen, and there is no need to specify the skeleton when specifying a template.

### Heading Levels

The `--heading-level` argument takes an integer *n* (which is 0 by default)
and shifts the heading level of `\section` (or `\chapter` if present) to a
level-*n* header. When not specified, `\section` will be mapped to `<h1>`.

For example, the following command will match all instances of
`\section` to `h2` headers, `\subsection` to `h3` headers,
`\subsubsection` to `h4` headers, and so on:

```
handcrab -i "Folder/MyInput.tex" -o "Folder2/MyOutput.html" -s sktn.html -hl 1
```

### Templates

There are certain CEMC resources that appear a lot, and have their own general look to them. A template has been designed for compiling all of the following resources, and it can be specified using the `--template` or `-t` argument:

| **Resource Name**   | **Template input** |
|---------------------|--------------------|
| BCC                 | `bcc`              |
| CCC/CCO             | `ccc`              |
| POTM                | `potm`             |
| Math Circles        | `mathcircles`      |
| all CTMC resources  | `ctmc`             |
| POTW                | `potw`             |
| Gauss Contest       | `gauss`            |
| Gauss Solution      | `gaussSoln`        |
| PCF Contests        | `pcf`              |
| PCF Solutions       | `pcfSoln`          |
| Euclid Contest      | `euclid`           |
| Euclid Solutions    | `euclidSoln`       |

Each template will automatically add any requisite arguments to
Handcrab in an attempt to make the desired output. Specifying
arguments will override the template. For example, the `ccc`
template automatically shifts heading levels down by 1, so if
your command was

```
handcrab -i filein.tex -o fileout.html -t ccc -hl 3
```

regardless of what `-t ccc` is doing to the heading levels,
the output will shift `\section` to `h4`. 

Certain templates have specific helper functions that help with
the latex and html processing. These can be disableed using the
`-dhf` or `--disable-helper-functions` parameter. `-dhf` will
have no effect if a template is not provided.

It should also be noted that the template input is case insensitive,
so `-t euclidSoln` is equivalent to `-t eUcLiDsOlN`. 

**The math circles template does not need specified outputs.**

#### Problem of the Week (POTW) conversion
The Problem of the Week files graphics and themes need specific commands in the LaTeX to trigger the "Theme" text and the fun-graphic alt text. To trigger the theme text, the following line must be added in the `ProblemDetails.tex` file:

```
\newcommand{\problemtheme}{theme goes here in lowercase}
```

If this line is either missing, or if the theme is left empty, the theme text **will not appear**.

The graphic is broken down into two parts:


- The resource uses `\pstoggle`
	- `\pstoggle` and all `fungraphic` macros are ignored
	- everything within `\problemonly` will be displayed regardless of problem or solution
- The resource does not use `\pstoggle`
	- The alt text is set to be empty and can only be modified in HTML. 

### Contest Title Notes
The level-1 header or title for contests does not necessarily
need to be provided for everything to compile. A default contest-title
template is provided, but by adding code such as

```.{multiline}
\begin{center}
\section{...}
...
\end{center}
```

the default will be overwritten with whatever is inside the center environment.

The `<title>...</title>` part of the HTML output will be exactly everything
within the `\section{...}` or `<h1>` tag, and will exclude any line breaks present.


#### PCF Contest and Solution Notes
As long as the contest name is in the filename, both the default title discussed
above, and the `Further Information` will have the correct contest name for the 
current contest and the next contest (referenced in "Encourage your teacher to
register you for ___ Contest")


## Installation/Dependencies
To run the program as a python script, the **lxml** python package has to be installed.
This is the package that handles XML parsing for updating table headers.

The following programs must also be installed

- Pandoc (used for converting processed LaTeX into HTML)
- TexLive-full (provides the pdflatex and pdfcrop commands, which are both used)
- Inkscape (used for converting tikz pdfs to svgs) 


## Environments

Handcrab offers extra conversion that pandoc doesn't do. The conversions
are specified by Handcrab's environments. For documentation and
examples, [click here](env.html)

## Handcrab LaTeX processing

Handcrab does some processing to the LaTeX code when compiling. Things such as removal of fboxes and phantoms. An in-depth explanation is [provided here](pre.html)

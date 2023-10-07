# Getting started

`pylingdocs` is a command line application and is executed by using
`pylingdocs <COMMAND> --<argument>` (if you\'re a wizard you can use
`the python API <modules>`{.interpreted-text role="doc"}). If you have
**no** previous exposure to command line interfaces, you may want to
read a guide [like
this](https://github.com/dictionaria/pydictionaria/blob/master/docs/intro-commandline.md)
or
[this](https://launchschool.com/books/command_line/read/introduction)[^1]
\-- though it appears you\'re handling linguistic databases already.
There is also an [rudimentary
editor](https://github.com/fmatter/pylingdocs-gui/) with a graphical
user interface.

## Quick start

1\. `pylingdocs new` will let you enter some data to get started with a project

:   -   if you\'re impatient, the only information truly needed is the
        path to a valid CLDF metadata.json file

2.  The project will live in a new folder, and inside you will find the
    [content]{.title-ref} folder. If you have installed Sublime Text,
    you can use `subl` to open the `<FILENAME>.sublime-project` file.
    Otherwise, use an editor of your choice to open one or all of the
    `.md` files.

3\. Get writing. You can use normal [markdown](https://www.markdownguide.org/cheat-sheet/), as well as [cldfviz](https://github.com/cldf/cldfviz/blob/main/docs/text.md) and `pylingdocs markdown <markdown_format>`{.interpreted-text role="doc"}.

:   -   if you are using Sublime Text and the `pylingdocs` plugin, you
        can use `pylingdocs sublime` in your project directory. This
        will activate autocompletion and also enable you to use
        `Tools > pylingdocs > insert entity` to add data points from
        your dataset.

4\. To create output, run `pylingdocs build` in the project folder. By default, a `range of output formats <data_formats>`{.interpreted-text role="doc"} will be produced, in the folder `output`

:   -   you can add the option `--latex` to create a PDF from the
        generated `.tex` file. Note: you need to have a working LaTeX
        installation with `latexmk` for this.

## Projects

A project minimally consists of a folder containing markdown files, a
YAML file describing how they should be combined, and a (link to a)
database containing the linguistic data. You can create a new project by
using `pylingdocs new` in the directory where you want your project
folder to be created. For the moment, a database can only consist of
`a CLDF dataset <data_formats>`{.interpreted-text role="doc"}.

### Multiple files

You can distribute your content into multiple files, which is often more
practical than a single file. The order of these files is described in a
[YAML](https://yaml.org/) file, defaulting to
\`contents/structure.yaml\`:: title: My fantastic book intro: title:
Introduction verbs: title: What is a verb, anyway? results: title: Turns
out, a lot comparison: title: Comparative verbistics abstract: You can
put abstracts here if you like! possession: title: Person marking
abstract: This is a part of the comparison chapter, but it\'s in its own
file. This would assume a file structure with 5 files, identified by
`intro`, `verbs`, `results`, `comparison`, and `possession`. When using
Sublime Text or some other editor that can open multiple text files but
doesn\'t know how to sort them, you can set the `content_file_prefix`
option to `alpha` or `numerical` and use `pylingdocs update-structure`
to rename your files. This will create filenames like `<[A-Z]> <ID>.md`
or `<\d\d\d\d> <ID>.md`.

You can also use the structure file to **create** files, by running
`update-structure`. Any `.md` files in the content folder that are not
in the structure file will be moved to a `bench` folder, in case you
want to include them again later (just put them in the structure file to
do so).

## Writing

Writing is done in plaintext, so you can use any old editor you like,
though I strongly recommend [Sublime Text](https://www.sublimetext.com/)
or [pylingdocs-gui](https://github.com/fmatter/pylingdocs-gui/). The
basic format used is [markdown](https://www.markdowntutorial.com/), with
some `magic sprinkled on top <markdown_format>`{.interpreted-text
role="doc"}. There is an [autocomplete
plugin](https://github.com/fmatter/pylingdocs-autocomplete-sublime) for
Sublime Text. If set up correctly, the plugin will show data preview
snippets when typing directives like `mp:<this_is_you_typing>`, and will
replace them with `[mp](id)`. There is also the functionality to insert
entities from your dataset via the \"Tools\" menu. `pylingdocs-gui` does
not have a database-editor connection yet.

### Preview

Since creating the database feeding a CLLD app or compiling LaTeX
documents can take some time, there is a preview function
(`pylingdocs preview`) which uses a lighter format (plaintext). This is
supposed to take away the burning uncertainty about what the commands
you\'re writing will correspond to in a document for humans. You can use
`pylingdocs preview --html` to open a preview in your browser or
`--latex` to create a pdf. You could also use the `github` format for
previews and then use [grip](https://pypi.org/project/grip/) for
previewing.

## Commands

The central and only necessary command is `pylingdocs build`, which
transforms the pylingdocs-flavored markdown into the specified output
formats. Below, the other commands are listed; you can also see them by
calling `pylingdocs --help`. For the default values of most arguments,
check out `the default config file <config>`{.interpreted-text
role="doc"}.

[^1]: You don\'t need any of the server stuff, though. Just get
    comfortable using the command line.

# Data formats

For the moment, [CLDF](https://cldf.clld.org/) is the only available
input format, via the [cldfviz](https://github.com/cldf/cldfviz/) tool.
However, it should not be difficult to implement support for other
formats, if needed.


# Markdown format

UNDER CONSTRUCTION

## Introduction

`pylingdocs` uses a custom markdown format. Access to entities in the
database (examples, morphemes, languages\...) is done in the format
`[abbr](id)`, where `abbr` represents the kind of entity, and `id` the
ID of the entity. So if you have an example with the ID `narr-23`, you
can include it in the text with the command `[ex](narr-23)`.

## Models

#TBD

## Citing and references

Citing sources is done by the commands `[src](bibkey[pages])` and
`[psrc](bibkey[pages])`. `bibkey` is the identifier of the source (for
example, a bibkey in a `.bib` file). `[pages]` is optional. For example,
`[src](meier2009example[229-231])` yields `Meier (2009: 229-231)`, and
`[psrc](meier2009example[229-231])` `(Meier 2009: 229-231)`.

## Other elements

### Tables

Every table has an ID; they can be inserted with the directive
`[table](id)`.

### Crossrefs

Crossrefs are not yet implemented.

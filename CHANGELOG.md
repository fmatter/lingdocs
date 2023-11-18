# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).


## [Unreleased]

## [0.1.3] - 2023-11-18

### Added
* [hypothe.is](https://hypothes.is/) functionality for HTML
* tags & index

### Fixed
* allow rich data when called from outside of folder
* project creation failure

### Changed
* table label in detail view
* I guess you can have output with links in it without writing all the data again
* simple HTML template

## [0.1.2] - 2023-10-27

### Added
* audio in mkdocs

### Changed
* much simpler custom format setup

### Fixed
* bug in CLDF creation
* HTML example IDs
* parsing glosses of the form `X._Y.` (multi-word glosses of single-word proper names)
* glossing abbreviations
* whitespace in LFTS macro
* template loading
* record numbers

## [0.1.1] - 2023-10-13

### Fixed
* the entire new project template
* a bug with the `-targets` argument
* `rich` option automatically makes `data` true

### Changed
* `extra` directory for user material
* also, preview reloading is sensitive to it
* `extra/landingpage.md` and `extra/<FORMAT>_landingpage.md`

## [0.1.0] - 2023-10-12

### Added
* [mkdocs](https://www.mkdocs.org/) template
* proper layout (`book`/`article`/`slides`) handling

### Fixed
* multipart LaTeX examples

### Changed
* more straightforward customization
* configuration with `.yaml` file rather than `.cfg`
* improved template loading
* mkdocs for documentation
* new [expex-acro](https://ctan.org/pkg/expex-acro) version
* `builders` settings is now named `build`
* makeover for CLI
* `contents` folder is now called `docs`

## [0.0.12] - 2023-07-02

### Added
* table of contents in markdown output
* option to choose LaTeX `book` template
* leipzig glossing abbreviations
* add additional external chapters when creating a CLDF dataset
* `topics_index.csv` will be added as a TopicTable
* `entity_refs.yaml` allows to add section references to entries in the database
* `full` argument for citations
* `bare` argument for exrefs
* one-stop solution for example layouting

### Fixed
* LaTeX examples
* handling of abbreviations
* revamped document commands
* abbrev checking
* lfts macro
* bib additions
* default table metadata
* datasets without sources work now

### Changed
* if undefined, `LATEX_TOPLEVEL` is determined based on the LaTeX template
* using [cldf-ldd](https://github.com/fmatter/cldf-ldd/)
* better HTML output

## [0.0.11] - 2022-11-27

### Added
* in the table metadata file, `header_column` can be set to `false` if the first column should be treated as a "content" column
* more sophisticated citing facilities
* cldf dataset creation with `ChapterTable`
* option to create sublime autocompletion data upon project initialization

### Removed

### Changed
* if a non-existing table is requested, a CSV file is generated
* HTML: smaller font sizes for titles
* HTML: center align figures
* HTML: more line spacing in table cells (when using line breaks)

### Fixed
* unglossed words don't throw errors

## [0.0.10] - 2022-10-15

### Added
* methods for reading and writing project configuration files

## [0.0.9] - 2022-09-19

### Changed
* more informative `check` function, now with offending files and lines
* `src` and `psrc` in clld table captions
* lowercase `paths` and `output` sections in config file

### Fixed
* preview function again
* apply cell decoration to content cells only
* don't apply cell decoration to empty cells
* `update-structure` adapted to new structure handling
* make relative path in setup wizard relative to CLDF dataset

## [0.0.8] - 2022-08-23

### Added
* sources in sublime text data

### Fixed
* preview function

## [0.0.7] - 2022-08-20

### Fixed

* default HTML pandoc output should be "html"

## [0.0.6] - 2022-08-20

### Added
* `pre_cell` and `post_cell` keywords in table metadata to apply markdown to entire table
* `pylingdocs author-config` command
* `add_bib` option for adding external sources
* figures functionality
* support for GUI editor
* experimental [reveal.js](https://revealjs.com/) output
* cognate set model & some templates
* cognate set coloring with @LinguList's JS code

### Removed
* text cldf metadata (now in [clld-corpus-plugin](https://github.com/fmatter/clld-corpus-plugin/blob/main/src/clld_corpus_plugin/cldf/TextTable-metadata.json))

### Changed
* simpler document structure

## [0.0.5] - 2022-07-21

### Added
* HTML preview with autorefresh
* preview in CLLD apps with [clld-document-plugin](https://github.com/fmatter/clld-document-plugin)
* `end` argument for crossrefs
* markdown in table captions
* section anchors for github
* language-form-translation-source template
* hide todos in releases

### Changed
* table metadata are stored in human-friendlier YAML

### Fixed
* don't split articles and slides
* whitespace in github output
* various small things

## [0.0.4] - 2022-06-03

### Added
* `todo` text command
* IGT examples as part of manual multipart examples
* `check` terminal command
* TOC in HTML output

### Removed
* bugs

### Changed
* nicer LaTeX memoir template

## [0.0.3] - 2022-05-27

### Added
* manual (i.e., non-interlinear) examples (`[manex](id)`)
* references in LaTeX and HTML IGT examples
* proper handling of glossing abbreviations in LaTeX and HTML output
* better exref commands (with arguments `end` and `suffix`)
* allow custom models and model templates
* allow custom output templates
* LaTeX memoir template

### Removed
* many small bugs

### Changed
* prettier LaTeX layouting
* HTML layout
* `wf` shortcut for forms
* relative file paths, `-source` should work now

## [0.0.2] - 2022-05-20

### Added
* generate data for the [Sublime Text plugin](https://github.com/fmatter/pylingdocs-sublime/) with `pylingdocs sublime`
* create a new project with `pylingdocs new`
* prettier plaintext example rendering
* use pandoc throughout
* expanded demo document
* multicite (LaTeX only, WIP)
* new options:
    * `readme`
    * `citation_cff`
* new default models:
    * Form
    * Cognateset
* new templates:
    * LaTeX `handout`
* `-latex` option for the `build` and `preview` commands
* `-release` option for better citability
* better HTML
* [expex-acro](https://github.com/fmatter/expex-acro/) in LaTeX templates

### Removed
* various bugs
* CITATION.CFF
* some CLDF metadata (now in [clld-morphology-plugin](https://github.com/fmatter/clld-morphology-plugin))

### Changed
* if the `structure_file` and `table_md` paths are only files, they are assumed to be in the content and tables folders, respectively 

## [0.0.1] - 2022-04-26

Initial release.

[Unreleased]: https://github.com/fmatter/pylingdocs/compare/v0.1.3...HEAD
[0.1.3]: https://github.com/fmatter/pylingdocs/compare/v0.1.2...v0.1.3
[0.1.2]: https://github.com/fmatter/pylingdocs/compare/v0.1.1...v0.1.2
[0.1.1]: https://github.com/fmatter/pylingdocs/compare/v0.1.0...v0.1.1
[0.1.0]: https://github.com/fmatter/pylingdocs/compare/0.0.12...v0.1.0
[0.0.12]: https://github.com/fmatter/pylingdocs/compare/0.0.11...0.0.12
[0.0.11]: https://github.com/fmatter/pylingdocs/compare/0.0.10...0.0.11
[0.0.10]: https://github.com/fmatter/pylingdocs/releases/tag/0.0.10
[0.0.9]: https://github.com/fmatter/pylingdocs/releases/tag/0.0.9
[0.0.8]: https://github.com/fmatter/pylingdocs/releases/tag/0.0.8
[0.0.7]: https://github.com/fmatter/pylingdocs/releases/tag/0.0.7
[0.0.6]: https://github.com/fmatter/pylingdocs/releases/tag/0.0.6
[0.0.5]: https://github.com/fmatter/pylingdocs/releases/tag/0.0.5
[0.0.4]: https://github.com/fmatter/pylingdocs/releases/tag/0.0.4
[0.0.3]: https://github.com/fmatter/pylingdocs/releases/tag/0.0.3
[0.0.2]: https://github.com/fmatter/pylingdocs/releases/tag/0.0.2
[0.0.1]: https://github.com/fmatter/pylingdocs/releases/tag/v0.0.1

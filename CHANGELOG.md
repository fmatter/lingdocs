# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).


## [Unreleased]

### Added
* `pre_cell` and `post_cell` keywords in table metadata to apply markdown to entire table
* `pylingdocs author-config` command
* `add_bib` option for adding external sources
* GUI editor
* figures functionality
* cognate set model

### Removed
* text cldf metadata (now in [clld-corpus-plugin](https://github.com/fmatter/clld-corpus-plugin/blob/main/src/clld_corpus_plugin/cldf/TextTable-metadata.json))

### Changed
* simpler document structure

### Fixed

## [0.0.5] -- 2022-07-21

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

## [0.0.4] -- 2022-06-03

### Added
* `todo` text command
* IGT examples as part of manual multipart examples
* `check` terminal command
* TOC in HTML output

### Removed
* bugs

### Changed
* nicer LaTeX memoir template

## [0.0.3] -- 2022-05-27

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
* relative file paths, `--source` should work now

## [0.0.2] -- 2022-05-20

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
* `--latex` option for the `build` and `preview` commands
* `--release` option for better citability
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

[Unreleased]: https://github.com/fmatter/pylingdocs/compare/0.0.5...HEAD
[0.0.5]: https://github.com/fmatter/pylingdocs/releases/tag/0.0.5
[0.0.4]: https://github.com/fmatter/pylingdocs/releases/tag/0.0.4
[0.0.3]: https://github.com/fmatter/pylingdocs/releases/tag/0.0.3
[0.0.2]: https://github.com/fmatter/pylingdocs/releases/tag/0.0.2
[0.0.1]: https://github.com/fmatter/pylingdocs/releases/tag/v0.0.1

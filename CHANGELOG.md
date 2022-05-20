# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

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

### Removed
* various bugs
* CITATION.CFF

### Changed
* if the `structure_file` and `table_md` paths are only files, they are assumed to be in the content and tables folders, respectively 

## [0.0.1] - 2022-04-26

Initial release.

[Unreleased]: https://github.com/fmatter/pylingdocs/compare/v0.0.1...HEAD
[0.0.1]: https://github.com/fmatter/pylingdocs/releases/tag/v0.0.1

# [pylingdocs](https://fl.mt/pylingdocs)

Create data-rich linguistic documents with CLDF, with a variety of output formats.

[![PyPI](https://img.shields.io/pypi/v/pylingdocs.svg)](https://pypi.org/project/pylingdocs)
![Versions](https://img.shields.io/pypi/pyversions/pylingdocs)
[![License](https://img.shields.io/github/license/fmatter/pylingdocs)](https://www.apache.org/licenses/LICENSE-2.0)
[![Tests](https://img.shields.io/github/actions/workflow/status/fmatter/pylingdocs/tests.yml?label=tests)](https://github.com/fmatter/pylingdocs/actions/workflows/tests.yml)
[![Changelog](https://img.shields.io/badge/keep_a-changelog-DC673D)](changes)

## About
Linguistic documents usually contain linguistic data, be it from primary research or sourced from the literature.
The primary function of pylingdocs is to make the integration of such data as simple as possible.
To achieve this, all data is stored in a [CLDF](https://cldf.clld.org/) dataset, while the accompanying prose is written in [markdown](https://www.markdownguide.org/).
This means that the document that contains no linguistic data, only pointers to the dataset.
Changes to the data only have to be done in the dataset, and don't include tinkering with the document.
Presentation of the data in the document is done by templates, 

 - no more manually italicizing object language forms.
The use of markdown and opinionated-but-customizable output templates results in [separation of content and presentation](https://en.wikipedia.org/wiki/Separation_of_content_and_presentation) in general.

To illustrate, [this plain text](https://github.com/fmatter/pylingdocs/blob/main/docs/demo.txt) in combination with [this dataset](https://github.com/fmatter/pylingdocs/tree/main/tests/data/cldf) can be turned into multiple formats:

* [PDF](https://github.com/fmatter/pylingdocs-demo/blob/main/doc/output/latex/main.pdf)
* [HTML](https://fmatter.github.io/pylingdocs-demo/) with [MkDocs](https://www.mkdocs.org/)
* [Github markdown](https://github.com/fmatter/pylingdocs-demo/tree/main/doc/output/github)
* and yes, even [plain text](https://github.com/fmatter/pylingdocs-demo/blob/main/doc/output/plain/document.txt)

It is also possible to integrate the output into [CLLD](https://clld.org/) web apps, using the [clld-document-plugin](https://github.com/fmatter/clld-document-plugin/); an example can be inspected [here](https://fl.mt/yawarana-sketch).

## 🔥 Quickstart

1. `pip install pylingdocs` ([full installation guide](https://fl.mt/pylingdocs/installation))
2. create or get a CLDF dataset
3. `pylingdocs new`, point to `metadata.json` file
4. `pylingdocs preview`
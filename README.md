# [lingdocs](https://fl.mt/lingdocs)

Create data-rich linguistic documents with CLDF, with a variety of output formats.

[![Versions](https://img.shields.io/pypi/pyversions/lingdocs?labelColor=4C566A&color=26619C)](https://www.python.org/)
[![PyPI](https://img.shields.io/pypi/v/lingdocs.svg?labelColor=4C566A&color=5E81AC)](https://pypi.org/project/lingdocs)
[![License](https://img.shields.io/github/license/fmatter/lingdocs?labelColor=4C566A&color=81A1C1)](https://www.apache.org/licenses/LICENSE-2.0)
[![Tests](https://img.shields.io/github/actions/workflow/status/fmatter/lingdocs/tests.yml?label=tests&labelColor=4C566A&color=8FBCBB)](https://github.com/fmatter/lingdocs/actions/workflows/tests.yml)
[![Changelog](https://img.shields.io/badge/changelog-v0.1.4-DC673D?labelColor=4C566A&color=88C0D0)](https://fl.mt/lingdocs/changes/)

## About
Linguistic documents usually contain linguistic data, be it from primary research or sourced from the literature.
The primary function of lingdocs is to make the integration of such data as simple as possible.
To achieve this, all data is stored in a [CLDF](https://cldf.clld.org/) dataset, while the accompanying prose is written in [markdown](https://www.markdownguide.org/).
This means that the document that contains no linguistic data, only pointers to the dataset.
Changes to the data only have to be done in the dataset, and don't include tinkering with the document.
Presentation of the data in the document is done by templates, 

 - no more manually italicizing object language forms.
The use of markdown and opinionated-but-customizable output templates results in [separation of content and presentation](https://en.wikipedia.org/wiki/Separation_of_content_and_presentation) in general.

To illustrate, [this plain text](https://github.com/fmatter/lingdocs/blob/main/docs/demo.txt) in combination with [this dataset](https://github.com/fmatter/lingdocs/tree/main/tests/data/cldf) can be turned into multiple formats:

* [PDF](https://github.com/fmatter/lingdocs-demo/blob/main/doc/output/latex/main.pdf)
* [HTML](https://fmatter.github.io/lingdocs-demo/) with [MkDocs](https://www.mkdocs.org/)
* [Github markdown](https://github.com/fmatter/lingdocs-demo/tree/main/doc/output/github)
* and yes, even [plain text](https://github.com/fmatter/lingdocs-demo/blob/main/doc/output/plain/document.txt)

It is also possible to integrate the output into [CLLD](https://clld.org/) web apps, using the [clld-document-plugin](https://github.com/fmatter/clld-document-plugin/); an example can be inspected [here](https://fl.mt/yawarana-sketch).

## 🔥 Quickstart

1. `pip install lingdocs` ([full installation guide](https://fl.mt/lingdocs/installation))
2. create or get a CLDF dataset
3. `lingdocs new`, point to `metadata.json` file
4. `lingdocs preview`
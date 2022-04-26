# pylingdocs

Create data-rich linguistic documents.

![License](https://img.shields.io/github/license/fmatter/pylingdocs)
[![Documentation Status](https://readthedocs.org/projects/pylingdocs/badge/?version=latest)](https://pylingdocs.readthedocs.io/en/latest/?badge=latest)
[![Tests](https://img.shields.io/github/workflow/status/fmatter/pylingdocs/tests?label=tests)](https://github.com/fmatter/pylingdocs/actions/workflows/tests.yml)
[![Linting](https://img.shields.io/github/workflow/status/fmatter/pylingdocs/lint?label=linting)](https://github.com/fmatter/pylingdocs/actions/workflows/lint.yml)
[![Codecov](https://img.shields.io/codecov/c/github/fmatter/pylingdocs)](https://app.codecov.io/gh/fmatter/pylingdocs/)
[![PyPI](https://img.shields.io/pypi/v/pylingdocs.svg)](https://pypi.org/project/pylingdocs)
![Versions](https://img.shields.io/pypi/pyversions/pylingdocs)

The main functionalities are showcased in the demo, consisting of a [PDF file](https://raw.githubusercontent.com/fmatter/pylingdocs/main/docs/demo.pdf) generated from [this text](https://github.com/fmatter/pylingdocs/blob/main/docs/demo.txt) and [this dataset](https://github.com/fmatter/pylingdocs/tree/main/tests/data/cldf).
The documentation lives at [pylingdocs.readthedocs.io](https://pylingdocs.readthedocs.io).

Note: currently the `pylingdocs` branch of `cldfviz` is needed, so to install you need to either:

`pip install git+https://github.com/fmatter/pylingdocs.git`

or

`pip install pylingdocs` and `pip install --upgrade git+https://github.com/cldf/cldfviz.git@pylingdocs`
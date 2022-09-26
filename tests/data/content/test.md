# Introduction [label](sec:intro)

This document does double service as a test for `pylingdocs` and a showcase of its capabilities.
It aims to demonstrate every feature and model currently available in `pylingdocs`.
The underlying `pylingdocs`-flavored markdown input can be found [here](https://github.com/fmatter/pylingdocs/blob/main/docs/demo.txt).
It uses data from the CLDF [test dataset](https://github.com/fmatter/pylingdocs/tree/main/tests/data/cldf).

We'll start with some generic markdown stuff.
Here is a link: [`pylingdocs`](https://github.com/fmatter/pylingdocs/).
Here is some **bold** and _italic_ text.

1. here
2. is
3. a
4. numbered
3. list

* and one
* with
* bullet points

Here's a cross reference to [ref](sec:linguistics).
Here's a cross reference[^3] to [ref](tab:onetable).

[^3]: And here is a (foot)note. You can use markdown in here: see [ref](sec:linguistics) for details about [mp](apa-se).

# Citing literature

`pylingdocs` supports citation styles commonly used in linguistics:

* [src](alvarez1998split)
* [psrc](alvarez1998split).
* [src](alvarez1998split[133-134])
* [psrc](alvarez1998split[133-134])
* [src](alvarez1998split[133-134],triomeira1999[218])
* [psrc](alvarez1998split[133-134],triomeira1999[218])
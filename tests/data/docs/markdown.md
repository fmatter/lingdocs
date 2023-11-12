# Common markdown
You can use all the familiar markdown components.
Here is a link to the [pylingdocs github repo](https://github.com/fmatter/pylingdocs/).
Here is some **bold** and _italic_ and **_bold italic_** text.

1. here
2. is
3. a
4. numbered
3. list

and of course here is

* one
* with
* bullet points[^3]

A quote:

> Locating an individual language on a given point of the ergativity-nominativity axis and the diachronic interpretation of this axis seem to be conceptually different concerns, even if we were to assume that there are principies favouring one direction over the other. [psrc](alvarez1998split[71])

[^3]: And here is a (foot)note. You can use markdown in here: see [ref](sec:data) for details about [mp](apa-se).

# Pylingdocs markdown [label](pld-md)

Apart from database references, discussed in [ref](sec:sources), there are a number of `pylingdocs`-specific commands, all patterning like links:

* cross-references: [ref](common-markdown) or [ref](sec:intro), see corresponding `label` commands
* example references:
    * single [exref](ekiri-13)
    * subexample [exref](ekiri-10)
    * range: [exref](ekiri-13?end=machete)
    * or bare: [exref](tri-1?bare)
* glosses: [gl](acc)
* todos: [todo](we need to talk about this)
* tables and figures (with automatically generated table labels like [ref](tab:consonants) and [ref](fig:cognates)):

[table](consonants)

[figure](cognates)
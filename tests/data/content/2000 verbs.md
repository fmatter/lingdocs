# Integrating linguistic entities [label](sec:linguistics)

The core functionality of `pylingdocs` is including linguistic data in your prose.
This is achieved by using the [`cldfviz`](https://github.com/cldf/cldfviz/) tool to access datasets in the [CLDF](https://cldf.clld.org/) format.
A number of models are built-in, at the moment:

1. morphemes: [mp](tri-se)
2. morphs: [m](tri-se-2)
3. languages: [lg](tri)
4. texts: [txt](ikp-ekiri)

You can also use cldfviz syntax: [Some label](LanguageTable#cldf:apa)


You can also refer to multiple entities of the same kind:
The [lg](tri) suffix [mp](tri-se) has the allomorphs [m](tri-se-1,tri-se-2,tri-se-3).
[lg](apa,tri) are both Cariban languages, as are [lg](pem,ikp,uxc).


## Interlinearized glossed examples

Glossed examples are called like any other entity, but are rendered as follows:

[ex](ekiri-1)

[ex](ekiri-2,ekiri-3)

Example references: [exref](ekiri-1), [exref](ekiri-3).

## Arguments
Pass arguments to the visualizer:

[ex](ekiri-4?example_id=my_custom_id&with_primaryText)
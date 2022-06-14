# Integrating linguistic entities [label](sec:linguistics)

The core functionality of `pylingdocs` is including linguistic data in your prose.
This is achieved by using the [`cldfviz`](https://github.com/cldf/cldfviz/) tool to access datasets in the [CLDF](https://cldf.clld.org/) format.
A number of models are built-in, at the moment:

1. morphemes: [mp](tri-se)
2. morphs: [m](tri-se-2)
3. languages: [lg](tri)
4. texts: [txt](ikp-ekiri)
5. forms: [wf](tri-fire)

You can use cldfviz syntax: [lg](apa) is the same as [Some label](LanguageTable#cldf:apa).

You can also refer to multiple entities of the same kind:
The [lg](tri) suffix [mp](tri-se) has the allomorphs [m](tri-se-1,tri-se-2,tri-se-3).
[lg](apa,tri) are both Cariban languages, as are [lg](pem,ikp,uxc).
This becomes very practical if you are citing data:

1. [wf](tri-fire,apa-fire,wai-fire?with_source&with_language)
1. [lg](tri) [wf](tri-with,tri-person,tri-us?with_source)

## Examples

### Interlinearized glossed examples

Glossed examples are inserted like any other entity, but are not rendered in-line:

[ex](ekiri-1)

[ex](ekiri-2,ekiri-3?example_id=mymultipartexample)

Example references should be versatile enough for most purposes: [exref](ekiri-1), [exref](ekiri-3), [exref](mymultipartexample), [exref](mymultipartexample?suffix=a-b), [exref](ekiri-1?end=mymultipartexample), [exref](mymultipartexample?suffix=arbitrarysuffix)

### Manual examples
These can contain tables, lists, whatever:

[manex](manex1)

They can also have multiple parts:

[manex](manex2)


## Arguments
Pass arguments to the visualizer, with examples:

[ex](ekiri-4?example_id=my_custom_id&with_primaryText)

[exref](my_custom_id)


Language labels, translations, and sources can be manipulated:

1. [mp](tri-se?with_language)
1. [m](tri-se-2?with_language)
1. [wf](tri-fire?with_language)

or

1. [mp](tri-se?with_source)
1. [m](tri-se-2?with_source)
1. [wf](tri-fire?with_source)

or

1. [mp](tri-se?no_translation)
1. [m](tri-se-2?no_translation)
1. [wf](tri-fire?no_translation)

or

1. [mp](tri-se?with_source&with_language)
1. [m](tri-se-2?with_source&with_language)
1. [wf](tri-fire?with_source&with_language)

or

1. [mp](tri-se?with_source&with_language&no_translation)
1. [m](tri-se-2?with_source&with_language&no_translation)
1. [wf](tri-fire?with_source&with_language&no_translation)

or

1. [mp](tri-se?with_source&with_language&translation=supine)
1. [wf](tri-fire?with_source&with_language&translation=people)

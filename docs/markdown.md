# Markdown

UNDER CONSTRUCTION

## Introduction

`lingdocs` uses a custom markdown format. Access to entities in the
database (examples, morphemes, languages\...) is done in the format
`[abbr](id)`, where `abbr` represents the kind of entity, and `id` the
ID of the entity. So if you have an example with the ID `narr-23`, you
can include it in the text with the command `[ex](narr-23)`.

## Models

## Citing and references

Citing sources is done by the commands `[src](bibkey[pages])` and
`[psrc](bibkey[pages])`. `bibkey` is the identifier of the source (for
example, a bibkey in a `.bib` file). `[pages]` is optional. For example,
`[src](meier2009example[229-231])` yields `Meier (2009: 229-231)`, and
`[psrc](meier2009example[229-231])` `(Meier 2009: 229-231)`.

## Interlinear examples

While lingdocs takes care of the formatting of examples, there are
some parameters you might want to modify. The following table shows the
basic layout; `[]` mark optional content.


  (exno)    |[LANGUAGE/TITLE   [SOURCE]]
  --------- |---------------------------------------
            |[PRIMARY TEXT]
            |OBJECT LINE
            |GLOSS LINE
            |'TRANSLATION'  [COMMENT]  [SOURCE]

### More complex examples
Sometimes, simply taking a single example from the dataset is not enough.
For instance, sometimes a table may be required in an example.
This can be achieved by creating a folder `manual_examples` in the working directory, creating a `<example-id>.md` file containing a table, and then using `[manex](example-id)` in the running text.

## Tables

Every table has an ID; they can be inserted with the directive
`[table](id)`.
A file with the name `<ID>.csv` must be placed in the `tables` directory.
Captions and other metadata is stored in `tables/metadata.yaml`.

## Figures

Every figure has an ID; they can be inserted with the directive
`[figure](id)`.
For figures, a caption and a filename must be provided in `figures/metadata.yaml`.
A file with the filename must be placed in the `figures` directory.

## Footnotes

Footnotes can be inserted with numbered `[^<ID>]`, usually something like `[^2]`; the content can then be defined on a later line with `[^<ID>]: <content>`.
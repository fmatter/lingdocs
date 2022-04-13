Markdown format
==================

UNDER CONSTRUCTION

Introduction
------------

``pylingdocs`` uses a custom markdown format.
Access to entities in the database (examples, morphemes, languages...) is done in the format ``[abbr](id)``, where ``abbr`` represents the kind of entity, and ``id`` the ID of the entity.
So if you have an example with the ID ``narr-23``, you can include it in the text with the command ``[ex](narr-23)``.


Models
-------
#TBD

Citing and references
------------------------

Citing sources is done by the commands ``[src](bibkey[pages])`` and ``[psrc](bibkey[pages])``.
``bibkey`` is the identifier of the source (for example, a bibkey in a ``.bib`` file).
``[pages]`` is optional.
For example, ``[src](meier2009example[229-231])`` yields ``Meier (2009: 229-231)``, and ``[psrc](meier2009example[229-231])`` ``(Meier 2009: 229-231)``.

Other elements
------------------

Tables
.......

Every table has an ID; they can be inserted with the directive ``[table](id)``.

Crossrefs
..........

Crossrefs are not yet implemented.
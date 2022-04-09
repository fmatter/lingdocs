Command line usage
===================

UNDER CONSTRUCTION

Introduction
------------

``pylingdocs`` is called from the command line, using the format ``pylingdocs <COMMAND> --<argument>``.
You can see a list of the following commands and what they do by calling ``pylingdocs --help``.
The central command is ``pylingdocs build``, which builds the specified output formats.

.. click:: pylingdocs.cli:main
   :prog: pylingdocs
   :nested: full
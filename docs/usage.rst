Usage
======

UNDER CONSTRUCTION

Introduction
------------

``pylingdocs`` is called from the command line, using the format ``pylingdocs <COMMAND> --<argument>``.

``pylingdocs`` projects
------------------------
A project minimally consists of a folder containing markdown files, and a data folder containing the linguistic data (:doc:`data_formats`).


You can see a list of the following commands and what they do by calling ``pylingdocs --help``.
The central command is ``pylingdocs build``, which builds the specified output formats.
For the default values of most arguments, look at the default config file in :doc:`config`.

.. click:: pylingdocs.cli:main
   :prog: pylingdocs
   :nested: full
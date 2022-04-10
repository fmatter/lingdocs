Usage
======

Introduction
------------

The easiest way to use ``pylingdocs`` is to use ``pylingdocs <COMMAND> --<argument>`` in a command line interface.
Editing is done in plaintext and can therefore happen in an editor of your choice, although I recommend `Sublime Text <https://www.sublimetext.com/>`_.
For the available kinds of output, see :doc:`output_formats`.

Projects
------------------------
A project minimally consists of a folder containing markdown files, a YAML file describing the structure of the document, and a database containing the linguistic data.
At the moment only CLDF is supported (:doc:`data_formats`), so the database consists of a CLDF dataset.

Document structure
^^^^^^^^^^^^^^^^^^^^
Document structure is described in YAML.

Commands
-----------------------

You can see a list of the following commands and what they do by calling ``pylingdocs --help``.
The central command is ``pylingdocs build``, which builds the specified output formats.
For the default values of most arguments, check out the default config file in :doc:`config`.

.. click:: pylingdocs.cli:main
   :prog: pylingdocs
   :nested: full
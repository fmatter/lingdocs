Usage
======

``pylingdocs`` is currently only available via a command line interface, using ``pylingdocs <COMMAND> --<argument>`` (if you're a wizard you can use :doc:`the python API <modules>`).
If you have **no** previous exposure to command line interfaces, you may want to read a guide `like this <https://launchschool.com/books/command_line/read/introduction>`_ [#]_ -- though it appears you're handling linguistic databases already.

.. contents:: Table of Contents
   :depth: 2
   :local:
   :backlinks: none


Quick start
-------------

1. ``pylingdocs new`` will let you enter some data to get started with a project
  * if you're impatient, the only information truly needed is the path to a valid CLDF metadata.json file
2. The project will live in a new folder, and inside you will find the `content` folder. If you have installed Sublime Text, you can use ``subl`` to open the ``<FILENAME>.sublime-project`` file. Otherwise, use an editor of your choice to open one or all of the ``.md`` files.
3. Get writing. You can use normal `markdown <https://www.markdownguide.org/cheat-sheet/>`_, and of course :doc:`pylingdocs markdown <markdown_format>`.
  * if you are using Sublime Text and the ``pylingdocs`` plugin, you can use ``pylingdocs sublime`` and then autocomplete or Tools > pylingdocs > insert entity to add data points from your dataset.
4. To create output, run ``pylingdocs build`` in the project folder. By default, a :doc:`range of output formats <data_formats>` will be produced, in the folder ``output``
  * you can add the option ``--latex`` to create a PDF from the generated ``.tex`` file. Note: you need to have a working LaTeX installation for this. 

Projects
------------------------
A project minimally consists of a folder containing markdown files, a YAML file describing how they should be combined, and a database containing the linguistic data.
You can create a new project by using ``pylingdocs new`` in the directory where you want your project folder to be created.
For the moment, a database can only consist of :doc:`a CLDF dataset <data_formats>`.

Multiple files
^^^^^^^^^^^^^^^^
You can distribure your content into multiple files, which -- depending on the extent of your megalomania -- is often more practical than a single file.
The order of these files is described in a `YAML <https://yaml.org/>`_ file, defaulting to `contents/structure.yaml`::
 document:
   title: My fantastic book
   parts:
     intro:
       title: Introduction
     verbs:
       title: What is a verb, anyway?
     results:
       title: Turns out, a lot
     comparison:
       title: Comparative verbistics
       abstract: You can put abstracts here if you like!
       parts:
         possession:
           title: Person marking
           abstract: This is a part of the comparison chapter, but it's in its own file.

This would assume a file structure with 5 files, identified by ``intro``, ``verbs``, ``results``, ``comparison``, and ``possession``.
When using Sublime Text or some other editor that can open multiple text files but doesn't know how to sort them, you can use ``pylingdocs update-structure`` to rename your files.
For this, the format ``<XXXX> <ID>.md`` is used, where ``XXXX`` is a number causing the files to be sorted correctly.
The above YAML file would result in this list of files::
  1000 intro.md
  2000 verbs.md
  3000 results.md
  4000 comparison.md
  4100 possession.md

You can also use the structure file to **create** files.
Any ``.md`` files in the content folder that are not in the structure file will be moved to the ``bench`` folder, in case you want to include them again later (just put them in the structure file).

Writing
--------
Writing is done in plaintext, so you can use any old editor you like, though I strongly recommend `Sublime Text <https://www.sublimetext.com/>`_. 
The basic format used is `markdown <https://www.markdowntutorial.com/>`_, with some :doc:`magic sprinkled on top <markdown_format>`.
There is an `autocomplete plugin <https://github.com/fmatter/pylingdocs-autocomplete-sublime>`_ for Sublime Text.
If set up correctly, the plugin will show data preview snippets when typing directives like ``mp:<this_is_you_typing>``, and will replace them with ``[mp](id)``.
There is also the functionality to insert entities from your dataset via the "Tools" menu.

Preview
^^^^^^^^
Since creating the database feeding a CLLD app or compiling LaTeX documents can take some time, there is a preview function (``pylingdocs preview``) which uses a lighter format (plaintext).
This is supposed to take away the burning uncertainty about what the commands you're writing will correspond to in a document for humans.
You could also use the ``github`` format for previews and then use `grip <https://pypi.org/project/grip/>`_ for previewing.

Commands
-----------------------


The central and only necessary command is ``pylingdocs build``, which transforms the pylingdocs-flavored markdown into the specified output formats.
Below, the other commands are listed; you can also see them by calling ``pylingdocs --help``.
For the default values of most arguments, check out :doc:`the default config file <config>`.

.. click:: pylingdocs.cli:main
   :prog: pylingdocs
   :nested: full

.. [#] Don't go for any of the server stuff, though. Just think about what each command does before you press enter.
# Customizing

It is possible to provide custom templates for both models and output formats.
It is also possible to create entirely new models and formats.
All custom content lives in a folder called `pld` in the project folder.

## Writing templates
Templates are written in [jinja](https://jinja.palletsprojects.com).

### Models
Model templates live in a directory `pld/model_templates/<model_name>`, where `model_name` is a lowercase singular version of the table (`morpheme`, `example`, `cognateset`...).
Each model has four views for which templates can be defined: inline, (inline) list, detail, index.
Filenames have the scheme `<format>_<view>.md`, where `format` is are names like `html` or `latex`, e.g.:

* `pld/model_templates/morph/html_list.md`: the inline list view for the morph model in HTML output
* `pld/model_templates/text/plain_inline.md`: the inline view for the text model in plaintext output

To get an idea of what model templates look like, check out the [built-in templates](https://github.com/fmatter/pylingdocs/tree/main/src/pylingdocs/data/model_templates).
There is a degree of inheritance in templates, so if e.g. `morph/github_detail` is not implemented, `morph/plain_detail`, `morpheme/plain_detail` and `morpheme/plain_detail` will also be tried -- the `morph` model inherits from `morpheme`, and the `github` output format inherits from `plain`.

### Formats
Format templates live in a directory `pld/format_templates/<format_name>/<template_name>` (e.g. `html/slides`).
They are [cookiecutter](https://cookiecutter.readthedocs.io) templates, so they minimally contain the files `cookiecutter.json` and a directory `{{cookiecutter.name}}`.
The contents of that folder will be in `output/<format>` when a project is compiled.
Built-in templates will be replaced entirely (not on a file-by-file basis), so it is suggested to copy the directory of one of the [built-in format templates](https://github.com/fmatter/pylingdocs/tree/main/src/pylingdocs/data/format_templates) and modify its contents.

## Creating formats
If you need to change more than just the format templates, you can create your own format in `pld/formats.py`.
Here is an example on how to create a modified HTML format, where todos are formatted differently, and figures are stored in a static folder.


```python
def custom_todo(url, **kwargs):
    return f"<span title='{url}'>TODO</span>"

class CustomHTML(HTML):
    name = "my_html_format"
    figure_dir = "static/figures"

    @classmethod
    def todo_cmd(cls, url, *_args, **_kwargs):
        return custom_todo(url, **_kwargs)

    @classmethod
    def figure_cmd(cls, url, *_args, **_kwargs):
        caption = cls.figure_metadata[url].get("caption", "")
        filename = cls.figure_metadata[url].get("filename", "")
        return f"""<figure>
<img src="static/figures/{filename}" alt="{caption}" />
<figcaption id="fig:{url}" aria-hidden="true">{caption}</figcaption>
</figure>"""

```

## Creating models
The file `pld/models.py` should be structured as follows:

```python
from pylingdocs.models import Base

class Phoneme(Base):
    name = "Phoneme"
    cldf_table = "phonemes.csv"
    shortcut = "pnm"

class POS(Base):
    name = "POS"
    cldf_table = "partsofspeech.csv"
    shortcut = "pos"

class Lexeme(Base):
    name = "Lexeme"
    cldf_table = "lexemes.csv"
    shortcut = "lex"


models = [Phoneme(), POS(), Lexeme()]

```

These are very minimal models, check out the [built-in models](https://github.com/fmatter/pylingdocs/blob/main/src/pylingdocs/models.py) for more examples.


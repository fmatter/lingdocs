{{ cookiecutter.project_title }}

This is the main file.

Here is a TOC:

{% for id, title in cookiecutter.parts.list.items() %}
* [{{ title }}]({{ id }}.md)
{% endfor %}

and here are refs:

{{ cookiecutter.references }}
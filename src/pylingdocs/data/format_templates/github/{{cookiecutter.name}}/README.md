{{ cookiecutter.project_title }}

This is the main file.

Here is a TOC:

{% for label, file in cookiecutter.parts.list.items() %}
* [{{ label }}]({{ file }})
{% endfor %}

and here are refs:

{{ cookiecutter.references }}
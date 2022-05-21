{% import 'util.md' as util %}
{% if ids is defined %}
    {% set ids = ids.split(",") %}
    {% set gathered_examples = {} %}
        {% for example in ctx %}
            {% if example.id in ids %}
                {% set _ = gathered_examples.update({example.id: example}) %}
            {% endif %}
        {% endfor %}
```{=latex}
\pex
{% for example_id in ids %}
{% set example = gathered_examples[example_id] %}
\a {{ example.related('languageReference').name }}\\
\label{% raw %}{{% endraw %}{{ example.id }}{% raw %}}{% endraw %}\begingl
\glpreamble {{ sanitize_latex(example.cldf.primaryText) }} //
{% if example.cldf.analyzedWord != [] %}
{% set objlist = [] %}
{% for o in example.cldf.analyzedWord %}
    {% set objlist = objlist.append(sanitize_latex(o)) %}
{% endfor %}
{% set glosslist = [] %}
{% for w in example.cldf.gloss %}
    {% set glosslist = glosslist.append(sanitize_latex(decorate_gloss_string(w))) %}
{% endfor %}
\gla {{ " ".join(objlist) }}//
\glb {{ " ".join(glosslist) }}//
{% endif %}
{% if example.cldf.translatedText != None %}
\glft ‘{{ example.cldf.translatedText }}’// {% endif %} 
\endgl 
{% endfor %}
\xe
```
{%else%}
no
{%endif%}



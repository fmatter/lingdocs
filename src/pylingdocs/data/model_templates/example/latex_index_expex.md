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
\a<{{ example.id }}> {{ example.related('languageReference').name }}\\
\begingl
\glpreamble {{ example.cldf.primaryText }} //
{% if example.cldf.analyzedWord != [] %}
{% set glosslist = [] %}
{% for w in example.cldf.gloss %}
    {% set glosslist = glosslist.append(w) %}
{% endfor %}
\gla {{ " ".join(example.cldf.analyzedWord) }}//
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



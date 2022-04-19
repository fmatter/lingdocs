{% import 'util.md' as util %}
{% if ids is defined %}
{%set ids = ids.split(",")%}
```{=latex}
\pex
{% for example in ctx %}
{% if example.id in ids %}
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
{% endif %}
{% endfor %}
\xe
```
{%else%}
no
{%endif%}



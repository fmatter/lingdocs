{% if ids is defined %}
{%set ids = ids.split(",")%}
{% set morphemes = [] %}
{% for morpheme in ctx %}
{% if morpheme.id in ids %}
{% set morphemes = morphemes.append(morpheme["Name"]) %}
{% endif %}
{% endfor %}
{{ comma_and_list(morphemes)}}{%endif%}
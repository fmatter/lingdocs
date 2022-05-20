{% macro examples(examples) -%}
{{examples}}
{%- endmacro %}

{% macro references(sources) -%}
{% set bibkey, pages = split_ref(sources[0].__str__()) %}
{% if pages %}
{% set page_string = "[" + pages + "]" %}
{% else %}
{% set page_string = "" %}
{% endif %}
\parencite{{page_string}}{%raw%}{{%endraw%}{{bibkey}}{%raw%}}{%endraw%}
{%- endmacro %}
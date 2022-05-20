{% macro examples(examples) -%}
{{examples}}
{%- endmacro %}

{% macro references(sources) -%}
{% set bibkey, pages = split_ref(sources[0].__str__()) %}
\parencite[{{pages}}]{%raw%}{{%endraw%}{{bibkey}}{%raw%}}{%endraw%}
{%- endmacro %}
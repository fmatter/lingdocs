{% macro translation(f, all_translations=True) -%}
{% if f.cldf.parameterReference is not string %} 
    {% set translations = [] %}
    {% for par in f.parameters %}
        {% set translations = translations.append(par.name) %}
    {% endfor %}
    {% set trans_string = translations|join(", ") %}
{% else %}
{% set trans_string = f.cldf.parameterReference %}
{% endif %}{{trans_string}}
{%- endmacro %}
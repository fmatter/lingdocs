{% macro get_translation_dict(f, all_translations=False) -%}
{% set translation = [] %}
{% for label in ["Meaning", "Translation"] %}
    {%if label in f%}
        {% if f[label] is not string %}
            {% for t in f[label] %}
                {% set translation = translation.append(t) %}
            {%endfor%}
        {%else%}
            {% set translation = translation.append(f[label]) %}
        {% endif %}
    {% endif %}
{% endfor %}
{%if all_translations%}{{" / ".join(translation)}}{%else%}{{translation[0]}}{%endif%}
{%- endmacro %}

{% macro get_translation_orm(f, all_translations=False) -%}
{% if f.parameters %}
    {% set translation = [] %}
    {%for p in f.parameters %}
        {% set translation = translation.append(p.name) %}
    {%endfor%}
{%if all_translations%}{{" / ".join(translation)}}{%else%}{{translation[0]}}{%endif%}
{%else%}
{{ get_translation_dict(f.data) }}
{%endif%}
{%- endmacro %}

{% macro lfts(
form_str,
entity=None,
with_language=False,
with_source=False,
no_translation=False,
mode="dict",
translation=None,
all_translations=Fall,
quot_left="‘",
quot_right="’",
citation_mode="cldfviz",
source_str=None
) -%}
{%if with_language %}{% if mode=="orm" %}{{entity.language.name}} {% else %}[](LanguageTable#cldf:{{entity["Language_ID"]}}) {%endif%}
{%endif%}
{{form_str}}{%if translation %} {{quot_left}}{{decorate_gloss_string(translation)}}{{quot_right}}{% elif not no_translation %}{% if mode=="orm" %} {{quot_left}}{{decorate_gloss_string(get_translation_orm(entity))}}{{quot_right}}{% else %} {{quot_left}}{{decorate_gloss_string(get_translation_dict(entity))}}{{quot_right}}{% endif %}{% endif %}
{% if source_str or with_source %}{%if mode == "orm" %} {{src(entity.references[0].__str__(), mode=citation_mode, parens=True)}}{%else%} {{src(entity["Source"], mode=citation_mode, parens=True)}}{%endif%}
{% endif %}
{%- endmacro %}
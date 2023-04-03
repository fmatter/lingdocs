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
\cite{{page_string}}{%raw%}{{%endraw%}{{bibkey}}{%raw%}}{%endraw%}
{%- endmacro %}

{% macro get_src_string (ctx, source=None) -%}
{% if source %}
{{source}}
{% elif ctx.references %}
{{references(ctx.references)}}
{% else %}
personal knowledge
{% endif %}
{%- endmacro %}


{% macro render_example(format, res) -%}
{% if format=="subexample" %}\a{%else%}\ex{%endif%} {%if res["preamble"]%}{{ res["preamble"] }} \\{%endif%}
\label{% raw %}{{% endraw %}{{ res["id"] }}{% raw %}}{% endraw %}
{% if res["obj"] != [] %}

\begingl {% if res["srf"] %}
\glpreamble {{ res["srf"] }} //{%endif%}
    {% set objlist = [] %}
    {% for o in res["obj"] %}
        {% set objlist = objlist.append(sanitize_latex(o)) %}
    {% endfor %}
    {% set glosslist = [] %}
    {% for g in res["gls"] %}
        {% set glosslist = glosslist.append(sanitize_latex(decorate_gloss_string(g))) %}
    {% endfor %}

\gla {{ " ".join(objlist) }}//
\glb {{ " ".join(glosslist) }}//
{% endif %}
\glft {{ sanitize_latex(res["ftr"]) }} \parentext{%raw%}{{%endraw%}{{res["postamble"]}}{%raw%}}{%endraw%}//
\endgl
{% if format=="subexample" %}{%else%}
\xe{%endif%}
{%- endmacro %}
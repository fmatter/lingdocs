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

{% macro txt_src(ctx) -%}
{% if data is undefined %}
{{ctx.data["Text_ID"]}}{% if ctx.data["Sentence_Number"] %}: {{ctx.data["Sentence_Number"]}}{%endif%}{% if ctx.data["Phrase_Number"] %} ({{ctx.data["Phrase_Number"]}}){%endif%}
{% else %}
{{link(data["examples"][ctx.id].text, anchor=ctx.id, html=True)}}{% if ctx.data["Sentence_Number"] %}: {{ctx.data["Sentence_Number"]}}{%endif%}
{% endif %}
{%- endmacro %}

{% macro get_src_string (ctx, source=None) -%}
{% if source %}
{{source}}{% elif ctx.references %}
{{references(ctx.references)}}{% elif "Text_ID" in ctx.data %}
{{txt_src(ctx)}}{% else %}
personal knowledge{% endif %}{%- endmacro %}

{% macro get_label(item, preferred="Name") %}
{{item.get(preferred, item.get("Form", item.get("Primary_Text", item.get("ID", "unknown"))))}}
{%- endmacro %}

{% macro render_example(format, res) -%}
{% if format=="subexample" %}

\a{%else%}\ex{%endif%} {% if res["title"] or res["posttitle"] %} {{ res["title"] }} {{ res["posttitle"] }} \\{%endif%}
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
\glft {{ sanitize_latex(res["ftr"]) }} {{res["postamble"]}}//
\endgl
{% if format=="subexample" %}{%else%}
\xe{%endif%}
{%- endmacro %}

{% macro link(item, anchor=None, html=False, preferred="Name") %}
{{get_label(item, preferred=preferred)}}
{%- endmacro %}
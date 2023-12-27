{% macro get_src_string (ctx, source=None) -%}
{% if source %}
{{source}}{% elif ctx.references %}
{% set ref = ctx.references[0] %}
{% set bibkey, pages = split_ref(ref.__str__()) %}
{% if pages %}
    {% set page_string = ": "+pages%}
{%else%}
    {% set page_string = ""%}
{% endif %}
<a href='site:references/#source-{{ref.source.id}}'>{{ref.source.refkey(year_brackets=None)}}</a>{{page_string}}{% elif "Text_ID" in ctx.data %}
{{txt_src(ctx)}}{% else %}
personal knowledge
{% endif %}
{%- endmacro %}


{% macro txt_src(ctx) -%}
{% if data is undefined %}
{{ctx.data["Text_ID"]}}{% if ctx.data["Record_Number"] %}: {{ctx.data["Record_Number"]}}{%endif%}
{% else %}
{{link(data["examples"][ctx.id].text, anchor=ctx.id, html=True)}}{% if ctx.data["Record_Number"] %}: {{ctx.data["Record_Number"]}}{%endif%}
{% endif %}
{%- endmacro %}



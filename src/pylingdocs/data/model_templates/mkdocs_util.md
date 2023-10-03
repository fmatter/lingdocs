{% macro render_example(class_, res) -%}
<li class={{class_}} id ="{{ res['id'] }}">
  <div class="interlinear-wrapper">
    <div class="preamble"> {{ res["title"] }} {{ res["posttitle"] }} </div>
    {%if res["srf"]%}
        <div class="text">{{ res["srf"] }}</div>
    {%else%}
         
    {%endif%}
    {% if res["obj"] != [] %}
      {% for obj in res["obj"] %}
        <div class="interlinear">
          <span class="obj">{{ obj }}</span>
            {% if res.get("obj2", []) != [] %}
              <span class="obj">{{ res["obj2"][loop.index-1] }}</span>
            {% endif %}
          <span class="gls">{{ decorate_gloss_string(res["gls"][loop.index-1]) }}</span>
          {%if "pos" in res %}<span class="pos">{{ res["pos"][loop.index-1]}}</span>{% endif %}
        </div>
      {% endfor %}
    {% endif %}
    <div class="ftr">{{ res["ftr"] }} {{res["postamble"]}} </div>
    {% set audio = None %}
    {% if audio %}
        <audio controls src="{{ audio['url'] }}" type="{{ audio['type'] }}"></audio>
    {% endif %}
  </div>
</li>
{%- endmacro %}

{% macro label(item) %}
{{item.get("Name", item.get("Form", item.get("Primary_ext", item.get("ID", "unknown"))))}}
{%- endmacro %}

{% macro link(item, anchor=None, html=False) %}
{% if anchor is not none %}
{% set anchor_text = "#"+anchor %}
{% endif %}
{% if item is not none %}
{% if html %}
<a href="site:data/{{item.table.label}}/{{item['ID']}}/{{anchor_text}}">{{label(item)}}</a>
{% else %}
[{{label(item)}}](site:data/{{item.table.label}}/{{item["ID"]}}/{{anchor_text}}){% endif %}
{% endif %}
{%- endmacro %}

{% macro txt_src(ctx) -%}
{% if ctx.data["Record_Number"] %}
{{link(data["examples"][ctx.id].text, anchor=ctx.id, html=True)}}: {{ctx.data["Record_Number"]}}{% else %}
{{link(data["examples"][ctx.id].text, anchor=ctx.id)}}{% endif %}
{%- endmacro %}

{% macro render_form(ctx) -%}
{% for part in ctx.wordformparts %}{{link(part.morph)}}{% endfor %}
{%- endmacro %}

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
<a href='/references/#source-{{ref.source.id}}'>{{ref.source.refkey(year_brackets=None)}}</a>{{page_string}}{% elif "Text_ID" in ctx.data %}
{{txt_src(ctx)}}{% else %}
{% endif %}
{%- endmacro %}


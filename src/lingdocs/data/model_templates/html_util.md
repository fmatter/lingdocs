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
          <span class="gls">{{ decorate_gloss_string(res["gls"][loop.index-1]) }}</span>
          {%if "pos" in res %}<span class="pos">{{ res["pos"][loop.index-1]}}</span>{% endif %}
        </div>
      {% endfor %}
    {% endif %}
    <div class="ftr">{{ res["ftr"] }} {{res["postamble"]}} </div>
    {% if res["audio"] %}
        <audio controls src="{{ res["audio"]['url'] }}" type="{{ res["audio"]['type'] }}"></audio>
    {% endif %}
  </div>
</li>
{%- endmacro %}

{% macro txt_src(data) -%}
{% if data["Sentence_Number"] %}
{{data["Text_ID"]}}: {{data["Sentence_Number"]}}{% else %}
{{data["Text_ID"]}}{% endif %}
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
<a href='#source-{{ref.source.id}}'>{{ref.source.refkey(year_brackets=None)}}</a>{{page_string}}{% elif "Text_ID" in ctx.data %}
{{txt_src(ctx.data)}}{% else %}
{% endif %}
{%- endmacro %}


{% macro get_label(item, preferred="Name") %}
{{item.get(preferred, item.get("Form", item.get("Primary_Text", item.get("Title", item.get("ID", "unknown")))))}}
{%- endmacro %}

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
    {% if res["audio"] %}
        <audio controls src="{{ res["audio"]['url'] }}" type="{{ res["audio"]['type'] }}"></audio>
    {% endif %}
  </div>
</li>
{%- endmacro %}

{% macro get_label(item, preferred="Name") %}
{{item.get(preferred, item.get("Form", item.get("Primary_Text", item.get("Title", item.get("ID", "unknown")))))}}
{%- endmacro %}

{% macro link(item, anchor=None, html=False, preferred="Name", label=None, prefix="data/", table_path=item.table.label) %}
{% if anchor is not none %}
{% set anchor_text = "#"+anchor %}
{% endif %}
{% if label is none %}
{% set label = get_rich_label(item, preferred=preferred) %}
{% endif %}
{% if item is not none %}
{% if html %}
<a href="site:{{prefix}}{{table_path}}/{{item['ID']}}/{{anchor_text}}">{{label}}</a>
{% else %}
[{{label}}](site:{{prefix}}{{table_path}}/{{item["ID"]}}/{{anchor_text}}){% endif %}
{% endif %}
{%- endmacro %}

{% macro txt_src(ctx) -%}
{%- if data is undefined %}
{{ctx.data["Text_ID"]}}{% if ctx.data["Sentence_Number"] %}: {{ctx.data["Sentence_Number"]}}{%endif%}
{% else %}
{{link(data["examples"][ctx.id].text, anchor=ctx.id, html=True)}}{% if ctx.data["Sentence_Number"] %}: {{ctx.data["Sentence_Number"]}}{%endif%}
{% endif %}
{%- endmacro %}

{% macro render_form(ctx) -%}
{% for part in ctx.wordformparts %}{{link(part.morph, html=True)}}{% endfor %}
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
<a href='site:references/#source-{{ref.source.id}}'>{{ref.source.refkey(year_brackets=None)}}</a>{{page_string}}{% elif "Text_ID" in ctx.data %}
{{txt_src(ctx)}}{% else %}
personal knowledge
{% endif %}
{%- endmacro %}

{% macro render_singles(rich) %}
{% for key, val in rich.fields.items() %}
    {% if (key is not in rich.foreignkeys and key is not in ["Tags", "References"] and val is not none)%}
        {% if key == "Segments"%} {%if val|length > 0 %}
            {% set val = " ".join(val) %}
* {{key}}: {{val}}
{%endif%}
        {% elif key == "Parameter_ID"%}{%if val|length > 0 %}
            {% set val = ", ".join(val) %}
* {{key}}: {{val}}
{%endif%}
        {% elif key == "Source"%} {%if val|length > 0 %}
            {% set val = src(val[0]) %}
* {{key}}: {{val}}
{%endif%}
        {% elif key == "Morpho_Segments" %}{%if val|length > 0 %}
            {% set val = "-".join(val) %}
* {{key}}: {{val}}
{%endif%}
        {% else %}
* {{key}}: {{val}}
        {% endif %}
    {% endif %}
{% endfor %}
{% for key, val in rich.single_refs.items() %}
{% if val is not none%}
* {{key.capitalize()}}: {{link(val)}}
{% endif %}
{% endfor %}
{% endmacro %}

{% macro render_multis(rich) %}
{% for key, values in rich.multi_refs.items() %}
    {% if values|length > 0 %}
        {% if key == "exampleparts" %}
=== "Examples"
        {% elif key == "wordformparts" and table_label(component)=="wordforms" %}
=== "Morphs"
        {% elif key == "stemparts" and table_label(component)=="morphs" %}
=== "Stems"
        {% elif key == "stemparts" and table_label(component)=="stems" %}
=== "Morphs"
        {% elif key in ["wordformstems", "tags"] %}
        {% elif key == "wordformparts" and table_label(component)=="morphs" %}
=== "Wordforms"
        {% else %}
=== "{{key.capitalize()}}"
        {% endif %}
    {% endif %}
    {% for val in values %}
        {% if key == "exampleparts" %}
    * {{link(val.example)}} ‘{{val.example["Translated_Text"]}}’
        {% elif key == "wordformparts" and table_label(component)=="wordforms" %}
    * {{lfts_link(val.morph)}}
        {% elif key == "wordformstems" %}
        {% elif key == "stemparts" and table_label(component)=="stems" %}
    * {{lfts_link(val.morph)}}
        {% elif key == "stemparts" and table_label(component)=="morphs" %}
    * {{lfts_link(val.stem)}}
        {% elif key == "wordformparts" and table_label(component)=="morphs" %}
    * {{lfts_link(val.wordform)}}
        {% elif key == "derivations" %}
    * {% if val.source is not none %}{{lfts_link(val.source)}}{%elif val.root is not none%}{{lfts_link(val.root)}}{%endif%} → {{lfts_link(val.target)}}
        {% elif key in ["wordformparts", "stems", "morphs", "lexemes", "morphemes", "forms", "wordforms"] %}
    * {{lfts_link(val)}}
        {% else %}
    * {{link(val)}}
          {% endif %}
    {% endfor %}
{% endfor %}
{% endmacro %}

{% macro render_example(class_, res) -%}
<li class={{class_}} id ="{{ res['id'] }}">
  <div class="interlinear">
    {{ res["preamble"] }}
    <div class="surf">{{ res["srf"] }}</div>
    {% if res["obj"] != [] %}
      {% for obj in res["obj"] %}
        <div class="intlin">
          <span class="obj">{{ obj }}</span>
          <span class="trans">{{ decorate_gloss_string(res["gls"][loop.index-1]) }}</span>
          {%if "pos" in res %}<span class="pos">{{ res["pos"][loop.index-1]}}</span>{% endif %}
        </div>
      {% endfor %}
    {% endif %}
    <div class="freetrans">{{ res["translation"] }} {%if res["postamble"] %} ({{ res["postamble"] }}) {%endif%}</div>
    {% set audio = None %}
    {% if audio %}
        <audio controls src="{{ audio['url'] }}" type="{{ audio['type'] }}"></audio>
    {% endif %}
  </div>
</li>
{%- endmacro %}

{% macro example(ctx,
class_="example",
example_id=None,
highlight=[],
title=None,
with_language=None,
comment=None,
source=None,
source_position=None,
show_primary=None) -%}
{% if ctx.references %}
    {% set ref = ctx.references[0] %}
    {% set bibkey, pages = split_ref(ref.__str__()) %}
{% endif %}
{% if source %}
    {% set src_string = "penis" %}
{% elif ref%}
{% set src_string = "<a href='#source-{{ref.source.id}}'>{{ref.source.refkey(year_brackets=None)}}</a>" %}
{% else %}
{% set src_string = "Personal knowledge" %}
{% endif %}
{% set res = build_example(
obj=ctx.cldf.analyzedWord,
gls=ctx.cldf.gloss,
ftr=ctx.cldf.translatedText,
txt=ctx.cldf.primaryText,
lng=ctx.related("languageReference").name,
src=src_string,
ex_id=example_id or ctx.cldf.id,
title=title,
show_language=with_language,
source_position=source_position,
show_primary=with_txt) %}
{{ render_example(class_, res) }}
{%- endmacro %}


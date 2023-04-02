{% macro render_example(class_, res) -%}
<li class={{class_}} id ="{{ res['id'] }}">
  <div class="interlinear-wrapper">
    <div class="preamble"> {{ res["preamble"] }} </div>
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
    <div class="ftr">{{ res["ftr"] }} {%if res["postamble"] %} ({{res["postamble"]}}) {%endif%}</div>
    {% set audio = None %}
    {% if audio %}
        <audio controls src="{{ audio['url'] }}" type="{{ audio['type'] }}"></audio>
    {% endif %}
  </div>
</li>
{%- endmacro %}

{% macro get_src_string (ctx, source=None) -%}
    {% if ctx.references %}
        {% set ref = ctx.references[0] %}
        {% set bibkey, pages = split_ref(ref.__str__()) %}
    {% endif %}
    {% if source %}
{{source}}
    {% elif ref%}
<a href='#source-{{ref.source.id}}'>{{ref.source.refkey(year_brackets=None)}}</a>
    {% else %}
personal knowledge{% endif %}
{%- endmacro %}

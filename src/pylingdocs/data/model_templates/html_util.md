{% macro example(ctx, class_="example", example_id=None) -%}
{% if ctx.references %}
{% set ref = ctx.references[0] %}
{% set bibkey, pages = split_ref(ref.__str__()) %}
<!--[{{bibkey}}](sources.bib?with_internal_ref_link&ref#cldf:{{bibkey}})"-->
{% endif %}
<li class={{class_}} id ="{{ example_id or ctx.id }}">
  <div class="interlinear">
    {{ ctx.related("languageReference").name }}
    {% if ctx.cldf.primaryText != None %} {% if ref%}(<a href="#source-{{ref.source.id}}">{{ref.source.refkey(year_brackets=None)}}</a>{%if ref.description%}: {{ref.description}}{%endif%})
{%endif%}
      <div class="surf">{{ ctx.cldf.primaryText }}</div>
    {% endif %}
    {% if ctx.cldf.analyzedWord != [] %}
      {% for obj in ctx.cldf.analyzedWord %}
        <div class="intlin">
          <span class="obj">{{ obj }}</span>
          <span class="trans">{{ decorate_gloss_string(ctx.cldf.gloss[loop.index-1]) }}</span>
        </div>
      {% endfor %}
    {% endif %}
    <div class="freetrans">‘{{ ctx.cldf.translatedText }}’
        </div>
  </div>
</li>
{%- endmacro %}
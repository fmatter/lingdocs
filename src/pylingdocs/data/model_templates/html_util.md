{% macro example(ctx, class_="example") -%}
<li class={{class_}} id ="{{ example_id or ctx.id }}">
  <div class="interlinear">
    {% if ctx.cldf.primaryText != None %}
      <div class="surf">{{ ctx.cldf.primaryText }}</div>
    {% endif %}
    {% if ctx.cldf.analyzedWord != [] %}
      {% for obj in ctx.cldf.analyzedWord %}
        <div class="intlin">
          <span class="obj">{{ obj }}</span>
          <span class="trans">{{ ctx.cldf.gloss[loop.index-1] }}</span>
        </div>
      {% endfor %}
    {% endif %}
    <div class="freetrans">‘{{ ctx.cldf.translatedText }}’</div>
  </div>
</li>
{%- endmacro %}
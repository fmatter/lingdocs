{# 
  Render an example object as IGT (if possible). 
  `with_primaryText`
  `with_internal_ref_link`
  `example_id`
  `as_table`
#}
{% import 'util.md' as util %}

<!-- adapted from https://linguistics.stackexchange.com/a/534 -->
<div class="interlinear">
({{ example_id or ctx.id }}) {% if ctx.cldf.primaryText != None %}
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
<div class="freetrans">‘{{ ctx.cldf.translatedText }}’</div><br>
</div>
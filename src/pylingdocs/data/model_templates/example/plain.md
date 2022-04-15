{# 
  Render an example object as IGT (if possible). 
  `with_primaryText`
  `with_internal_ref_link`
  `example_id`
#}
{% import 'util.md' as util %}

({{ example_id or ctx.id }}) {{ ctx.related('languageReference').name }}

{% if (ctx.cldf.analyzedWord == [] or with_primaryText) and ctx.cldf.primaryText != None %}
{{ ctx.cldf.primaryText }}
{% endif %}
{% if ctx.cldf.analyzedWord != [] %}
{% set obj, gloss = pad_ex(ctx.cldf.analyzedWord, ctx.cldf.gloss) %}
{{ obj }}  
{{ gloss }}  
{% endif %}
{% if ctx.cldf.translatedText != None %}
‘{{ ctx.cldf.translatedText }}’{% endif %}
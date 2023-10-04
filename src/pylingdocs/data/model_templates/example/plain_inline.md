{# 
  Render an example object as IGT (if possible). 
  `with_primaryText`
  `with_languageLabel`
  `with_internal_ref_link`
  `label`
  `build_example`
  `title`
  `source`
#}
{% set data = build_example(
    dict(obj=ctx.cldf.analyzedWord,
    gls=ctx.cldf.gloss,
    ftr=ctx.cldf.translatedText,
    show_language=with_languageLabel,
    show_primary=with_primaryText,
    src="source",
    title=title)
) %}

[ex-{{ label or ctx.id }}] {{ header }} ({{ ctx.id }})  
{% if (ctx.cldf.analyzedWord == [] or show_primary) and ctx.cldf.primaryText != None %}{{ ctx.cldf.primaryText }}
{% endif %}
{% if ctx.cldf.analyzedWord != [] %}
{% set obj, gloss = pad_ex(ctx.cldf.analyzedWord, ctx.cldf.gloss) %}
{{ obj.replace(" ", "|WHITESPACE|") }}  
{{ gloss.replace(" ", "|WHITESPACE|") }}  
{% endif %}
{% if ctx.cldf.translatedText != None %}
‘{{ ctx.cldf.translatedText }}’{% endif %} {{ post_translation }}


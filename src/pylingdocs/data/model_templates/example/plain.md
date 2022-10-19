{# 
  Render an example object as IGT (if possible). 
  `with_primaryText`
  `with_languageLabel`
  `with_internal_ref_link`
  `label`
  `get_example_data`
  `title`
  `source`
#}
{% import 'util.md' as util %}
{% set header, show_primary, post_translation = get_example_data(
    ctx.language.name,
    show_language=with_languageLabel,
    show_primary=with_primaryText,
    source_string="my source yes",
    title=title
) %}

({{ label or ctx.id }}) {{ header }}  
{% if (ctx.cldf.analyzedWord == [] or show_primary) and ctx.cldf.primaryText != None %}{{ ctx.cldf.primaryText }}
{% endif %}
{% if ctx.cldf.analyzedWord != [] %}
{% set obj, gloss = pad_ex(ctx.cldf.analyzedWord, ctx.cldf.gloss) %}
{{ obj.replace(" ", "|WHITESPACE|") }}  
{{ gloss.replace(" ", "|WHITESPACE|") }}  
{% endif %}
{% if ctx.cldf.translatedText != None %}
‘{{ ctx.cldf.translatedText }}’{% endif %} {{ post_translation }}


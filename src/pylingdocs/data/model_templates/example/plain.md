{# 
  Render an example object as IGT (if possible). 
  `with_primaryText`
  `with_internal_ref_link`
  `example_id`
  `get_example_data`: obligatory
  `title`
  `source`
#}
{% import 'util.md' as util %}
{% set example_data = get_example_data(
    ctx.related('languageReference').name,
    title,
    ref_string=util.reference(ctx.references[0]),
    corpus_string=ctx.data["Text_ID"],
    custom_source=source
) %}
({{ example_id or ctx.id }}) {{example_data["title"]}} ({{ ctx.id }})  
{% if (ctx.cldf.analyzedWord == [] or with_primaryText) and ctx.cldf.primaryText != None %}{{ ctx.cldf.primaryText }}
{% endif %}
{% if ctx.cldf.analyzedWord != [] %}
{% set obj, gloss = pad_ex(ctx.cldf.analyzedWord, ctx.cldf.gloss) %}
{{ obj.replace(" ", "|WHITESPACE|") }}  
{{ gloss.replace(" ", "|WHITESPACE|") }}  
{% endif %}
{% if ctx.cldf.translatedText != None %}
‘{{ ctx.cldf.translatedText }}’{% endif %} ({{example_data["source"]}})  


{# 
  Render an example object as IGT (if possible). 
  `build_example`: obligatory
  `with_primaryText`
  `with_language`
  `example_id`
  `format`
  `title`
  `comment`
  `source`
#}
{% import 'fmt_util.md' as util %}
{% set data = dict(
    obj=ctx.cldf.analyzedWord,
    gls=ctx.cldf.gloss,
    ftr=ctx.cldf.translatedText,
    txt=ctx.cldf.primaryText,
    lng=ctx.related("languageReference").name,
    src=util.get_src_string(ctx, source=source),
    ex_id=example_id or ctx.cldf.id,
    title=title,
    comment=comment,
    show_language=with_language,
    source_position=src_pos,
    show_primary=with_primaryText
) %}
```{=latex}
{{ util.render_example(class_, build_example(data))}}
```
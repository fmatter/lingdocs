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
{% if format=="subexample" %}
    {% set class_="subexample" %}
{% else %}
    {% set class_="example" %}
{% endif %}
{% set data=dict(
    obj=ctx.cldf.analyzedWord,
    gls=ctx.cldf.gloss,
    ftr=ctx.cldf.translatedText,
    txt=ctx.cldf.primaryText,
    lng=ctx.related("languageReference").name,
    src=util.get_src_string(ctx, source),
    ex_id=example_id or ctx.cldf.id,
    title=title,
    comment=comment,
    show_language=with_language,
    source_position=src_pos,
    show_primary=with_primaryText,
    audio=get_audio(ctx.cldf.mediaReference)
    ) %}
```{=html}
<ol class="{{class_}}">
{{ util.render_example(class_, build_example(data))}}
{% if class_=="example" %}
</ol>
```
{% endif %}
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
{% import 'pld_util.md' as util %}
```{=html}
{% if format=="subexample" %}
    {% set class_="subexample" %}
{% else %}
    {% set class_="example" %}
    <ol class="example">
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
    show_primary=with_primaryText
    ) %}
{{ util.render_example(class_, build_example(data))}}
{% if class_=="example" %}
</ol>
{% endif %}
```

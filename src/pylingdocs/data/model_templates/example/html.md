{# 
  Render an example object as IGT (if possible). 
  `example_id`
  `format`
  `with_language`
  `title`
  `comment`
  `source`
#}
{% import 'html_util.md' as util %}
```{=html}
{% if format=="subexample" %}
    {% set class_="subexample" %}
{% else %}
    {% set class_="example" %}
    <ol class="example">
{% endif %}
{{ util.example(ctx,
    example_id=example_id,
    title=title,
    comment=comment,
    source=source,
    with_language=with_language,
    source_position=src_pos,
    show_primary=with_txt
    )
}}
{% if class_=="example" %}
</ol>
{% endif %}
```

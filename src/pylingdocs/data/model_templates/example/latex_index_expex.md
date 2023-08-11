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
{% if ids is defined %}
    {% set ids = ids.split(",") %}
    {% set gathered_examples = [] %}
        {% for example in ctx %}
            {% if example.id in ids %}
                {% set _ = gathered_examples.append(dict(
    obj=example.cldf.analyzedWord,
    gls=example.cldf.gloss,
    ftr=example.cldf.translatedText,
    txt=example.cldf.primaryText,
    lng=example.related("languageReference").name,
    src=util.get_src_string(example, source=source),
    ex_id=example_id or example.cldf.id,
    title=title,
    comment=comment,
    show_language=with_language,
    source_position=src_pos,
    show_primary=with_primaryText
)) %}
            {% endif %}
        {% endfor %}
{% endif %}

{% set example_data, preamble = build_examples(gathered_examples) %}

```{=latex}
\ex{% if preamble %} {{ preamble }}{% endif %}
{% for example in example_data %}
    {{util.render_example("subexample", example)}}
{%endfor %}
\xe
```
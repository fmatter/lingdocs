{# 
  Render an example object as IGT (if possible). 
  `example_id`
  `format`
  `with_language`
#}
{% import 'html_util.md' as util %}
{%if format=="subexample"%}
```{=html}
{{ util.example(ctx, example_id="irrelevant", class_="subexample", with_language=with_language) }}
```
{%else%}
```{=html}
<ol class="example">
{{ util.example(ctx, example_id=example_id, with_language=with_language) }}
</ol>
```
{%endif%}

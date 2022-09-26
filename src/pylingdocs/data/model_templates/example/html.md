{# 
  Render an example object as IGT (if possible). 
  `example_id`
  `format`
#}
{% import 'html_util.md' as util %}
{%if format=="subexample"%}
```{=html}
{{ util.example(ctx, example_id="irrelevant", class_="subexample") }}
```
{%else%}
```{=html}
<ol class="example">
{{ util.example(ctx, example_id=example_id) }}
</ol>
```
{%endif%}

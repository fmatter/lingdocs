{# 
  Render an example object as IGT (if possible). 
  `example_id`
#}
{% import 'html_util.md' as util %}
```{=html}
<ol class="example">
{{ util.example(ctx) }}
</ol>
```
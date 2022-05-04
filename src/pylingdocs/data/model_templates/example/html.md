{# 
  Render an example object as IGT (if possible). 
  `with_primaryText`
  `with_internal_ref_link`
  `example_id`
  `as_table`
#}
{% import 'html_util.md' as util %}
<!-- adapted from https://linguistics.stackexchange.com/a/534 -->
```{=html}
<ol class="example">
{{ util.example(ctx) }}
</ol>
```
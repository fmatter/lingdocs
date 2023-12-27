{% import "fmt_util.md" as util%}
{{table_label(component)}}

{% for rec in ctx %}
- {{util.get_label(rec)}}
{% endfor %}
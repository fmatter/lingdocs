{% import "fmt_util.md" as util%}
{{table}}

{% for rec in ctx %}
- {{util.get_label(rec)}}
{% endfor %}
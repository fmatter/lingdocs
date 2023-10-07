{% import "pld_util.md" as pld_util%}
{% import "fmt_util.md" as util%}

{% for rec in ctx %}
* {{util.link(data[table_label(component)][rec.id])}}
{% endfor %}
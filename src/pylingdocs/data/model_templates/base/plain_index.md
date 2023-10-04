{% import "pld_util.md" as util%}
{{ table.label }}
{% for key, ctx in table.records.items(): %}

{% for k, v in ctx.items() %}
{% if v %}
* {{k}}: {{v}}
{% endif %}

{% endfor %}

{% endfor %}
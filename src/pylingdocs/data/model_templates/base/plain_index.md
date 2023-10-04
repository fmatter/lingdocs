{% import "util.md" as util%}

{% for rec in ctx %}
{{util.link(rec)}}
{% endfor %}
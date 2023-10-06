{% import 'pld_util.md' as pld_util%}
{% import 'fmt_util.md' as util%}

# {{table.capitalize()}}
{% for item in ctx %}
{% set rich = data[table][item["ID"]] %}
* util.link(rich)
{% endfor %}
{% import 'pld_util.md' as util%}
{% import 'fmt_util.md' as butil%}

# {{table.capitalize()}}
{% for item in ctx %}
{% set rich = data[table][item.get("ID", item.id)] %}
* {{butil.link(rich)}}
{% endfor %}
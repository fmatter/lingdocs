{% import 'pld_util.md' as util%}
{% import 'fmt_util.md' as butil%}

# {{table.capitalize()}}
{% for item in ctx %}
{% set rich = data[table][item["ID"]] %}
* {{pld_util.lfts(util.link(rich), entity=rich.fields, with_translation=True)}}
{% endfor %}
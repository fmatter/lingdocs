{% import 'pld_util.md' as pld_util%}
{% import 'fmt_util.md' as util%}

# {{table_label(component).capitalize()}}
{% for item in ctx %}
{% set rich = data[table_label(component)][item["ID"]] %}
* {{pld_util.lfts(util.link(rich), entity=rich.fields, with_translation=True)}}
{% endfor %}
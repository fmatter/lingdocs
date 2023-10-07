{% import 'pld_util.md' as pld_util%}
{% import 'fmt_util.md' as util%}

# {{table_label(component).capitalize()}}
{% for item in ctx %}
{% set rich = data[table_label(component)][item["ID"]] %}
* {{lfts_link(rich, with_translation=True)}}
{% endfor %}
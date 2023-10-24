{% import 'fmt_util.md' as util %}
{% set rich = data[table_label(component)][ctx["ID"]] %}

# {{table_label(component,mode="singular").capitalize()}}: {{util.get_label(rich)}}
TBD
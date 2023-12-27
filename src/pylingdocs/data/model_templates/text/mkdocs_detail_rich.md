{% import 'fmt_util.md' as util %}
{% set rich = data[table_label(component)][ctx["ID"]] %}

# {{table_label(component,target="single").capitalize()}}: {{util.get_label(rich)}}


{% for tex in rich.multi_refs["examples"] %}
[](ExampleTable#cldf:{{tex["ID"]}})
{% endfor %}

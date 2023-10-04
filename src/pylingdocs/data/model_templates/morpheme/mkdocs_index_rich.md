# {{table.label.capitalize()}}
{% import 'pld_util.md' as util %}
{% for key, item in table.records.items(): %}
* {{util.link(item)}}
{% endfor %}
# {{table.label.capitalize()}}
{% import 'util.md' as util %}
{% for key, item in table.records.items(): %}
* {{util.link(item)}}
{% endfor %}
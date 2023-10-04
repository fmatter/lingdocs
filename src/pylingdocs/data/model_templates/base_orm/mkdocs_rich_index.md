{% import 'util.md' as util %}
{% for key, item in table.entries.items(): %}
* {{util.link(item)}}
{% endfor %}
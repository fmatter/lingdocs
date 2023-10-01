{% import 'pld_util.md' as util %}

# {{table.name}}
{% for key, item in table.entries.items(): %}
* {{util.link(item)}}
{% endfor %}
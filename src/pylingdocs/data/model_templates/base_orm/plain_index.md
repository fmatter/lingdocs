# {{ table.label }}
{% for key, item in table.entries.items(): %}
* {{item}}
{% endfor %}
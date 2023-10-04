# {{ table.label }}
{% for key, item in table.records.items(): %}
* {{item}}
{% endfor %}
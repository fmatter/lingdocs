{% macro label(item, preferred="Name") %}
{{item.get(preferred, item.get("Form", item.get("Primary_Text", item.get("ID", "unknown"))))}}
{%- endmacro %}

{% macro link(item, anchor=None, html=False) %}
{% if item is not none %}
[{{label(item)}}](site:data/{{item.table.label}}/{{item["ID"]}}/{{anchor_text}}){% endif %}
{%- endmacro %}
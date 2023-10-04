{% macro label(item, preferred="Name") %}
{{item.get(preferred, item.get("Form", item.get("Primary_Text", item.get("ID", "unknown"))))}}
{%- endmacro %}

{% macro link(item, anchor=None, html=False) %}{%- endmacro %}
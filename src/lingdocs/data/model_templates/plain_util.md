{% macro get_label(item, preferred="Name") %}
{{item.get(preferred, item.get("Form", item.get("Primary_Text", item.get("ID", "unknown"))))}}
{%- endmacro %}

{% macro link(item, anchor=None, html=False, preferred="Name") %}
{{get_label(item, preferred=preferred)}}
{%- endmacro %}
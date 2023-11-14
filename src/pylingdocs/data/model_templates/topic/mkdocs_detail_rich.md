{% import 'fmt_util.md' as util %}
{% set rich = data[table_label(component)][ctx["ID"]] %}
{% if rich.get("Tags") %}---
tags:{% for tag in rich["Tags"]%}

  - {{tag}}{%endfor%}

---

{%endif%}
# {{table_label(component,target="single").capitalize()}}: {{util.get_label(rich)}}

{{rich["Description"]}}

{% for ref in rich["References"] %}
* [{{ref["Label"]}}](site:{{ref["Chapter"]}}#{{ref["ID"]}})
{% endfor %}
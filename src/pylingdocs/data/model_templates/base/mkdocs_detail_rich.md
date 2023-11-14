{% import 'fmt_util.md' as util %}
{% set rich = data[table_label(component)][ctx["ID"]] %}
{% if rich.get("Tags") %}---
tags:{% for tag in rich["Tags"]%}

  - {{tag}}{%endfor%}

---

{%endif%}
# {{table_label(component,target="single").capitalize()}}: {{util.get_label(rich)}}
{{util.render_singles(rich)}}
{{util.render_multis(rich)}}
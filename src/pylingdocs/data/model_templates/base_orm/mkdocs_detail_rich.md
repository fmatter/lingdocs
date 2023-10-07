{% import 'fmt_util.md' as util %}
{% set rich = data[table_label(component)][ctx.id] %}

# {{util.get_label(rich)}}
{{util.render_singles(rich)}}
{{util.render_multis(rich)}}
{% import 'pld_util.md' as pld_util %}
{% import 'fmt_util.md' as util %}
{% set rich = data[table_label(component)][ctx["ID"]] %}

# {{pld_util.lfts(util.get_label(rich), entity=rich.fields, with_translation=True)}}


{{util.render_singles(rich)}}


{{util.render_multis(rich)}}
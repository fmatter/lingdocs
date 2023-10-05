{% import 'pld_util.md' as pld_util %}
{% import 'fmt_util.md' as util %}
{% set rich = data[table][ctx["ID"]] %}

# {{pld_util.lfts(util.link(rich), entity=rich.fields, translation=rich.parameter[0]["Description"])}}
{{util.render_singles(rich)}}
{{util.render_multis(rich)}}
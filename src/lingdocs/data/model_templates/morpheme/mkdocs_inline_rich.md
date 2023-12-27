{% import 'pld_util.md' as util%}
{% import 'fmt_util.md' as butil%}
{% set rich = data[table_label(component)][ctx["ID"]] %}
{{lfts_link(rich,translation=translation,source=source,with_language=with_language,with_translation=with_translation,with_source=with_source)}}
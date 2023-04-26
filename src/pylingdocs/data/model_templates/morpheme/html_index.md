{% import 'pylingdocs_util.md' as util%}
{% if ids is defined %}
{%set ids = ids.split(",")%}
{% set morphemes = [] %}
{% for morpheme in ctx %}
{% if morpheme.id in ids %}
{% set morphemes = morphemes.append(
    util.lfts(
    "<i>"+morpheme["Name"]+"</i>",
    entity=morpheme,
    translation=translation,
    source=source,
    with_language=with_language or lfts["show_lg"],
    with_source=with_source or lfts["show_src"],
    no_translation=no_translation or not lfts["show_ftr"],
    )
)
%}
{% endif %}
{% endfor %}
{{ comma_and_list(morphemes)}}{%endif%}
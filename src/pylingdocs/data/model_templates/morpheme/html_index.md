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
    with_language=with_language or False,
    with_source=with_source or False,
    source_str=source_str,
    no_translation=no_translation,
    translation=translation
    )
)
%}
{% endif %}
{% endfor %}
{{ comma_and_list(morphemes)}}{%endif%}
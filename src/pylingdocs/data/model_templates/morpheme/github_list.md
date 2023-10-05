{% import 'pld_util.md' as util %}
{% if ids is defined %}
{%set ids = ids.split(",")%}
{% set morphemes = [] %}
{% for morpheme in ctx %}
{% if morpheme.id in ids %}
{% set morphemes = morphemes.append(util.lfts(
    "_"+morpheme["Name"]+"_",
    entity=morpheme,
    translation=translation,
    source=source,
    with_language=with_language,
    with_source=with_source,
    with_translation=with_translation,
)) %}
{% endif %}
{% endfor %}
{{ comma_and_list(morphemes)}}{%endif%}
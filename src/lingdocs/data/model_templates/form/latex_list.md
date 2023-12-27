{% import 'pld_util.md' as util%}
{% set my_list = [] %}
{%for f in ctx%}
{%if f.id in ids%}
{% set my_list = my_list.append(util.lfts(
    "\obj{"+f.cldf.form+"}",
    entity=f,
    translation=translation,
    source=source,
    with_language=with_language,
    with_source=with_source,
    with_translation=with_translation,
    citation_mode="biblatex",
    mode="orm"
)) %}
{%endif%}
{%endfor%}
{{comma_and_list(my_list)}}
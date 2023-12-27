{% import 'pld_util.md' as util%}
{% set my_list = [] %}
{%for f in ctx%}
{%if f.id in ids%}
{% set my_list = my_list.append(util.lfts(
    f.cldf.form,
    entity=f,
    translation=translation,
    with_language=with_language,
    with_source=with_source,
    with_translation=with_translation,
    source=source,
    mode="orm"
)) %}
{%endif%}
{%endfor%}
{{comma_and_list(my_list)}}
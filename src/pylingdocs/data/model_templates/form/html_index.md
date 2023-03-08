{% import 'pylingdocs_util.md' as util%}
{% set my_list = [] %}
{%for f in ctx%}
{%if f.id in ids%}
{% set my_list = my_list.append(util.lfts(
    "<i>"+f.cldf.form+"</i>",
    entity=f,
    with_language=with_language,
    with_source=with_source,
    translation=translation,
    no_translation=no_translation,
    source_str=source_str,
    mode="orm"
)) %}
{%endif%}
{%endfor%}
{{comma_and_list(my_list)}}
{# 
  Render an example object as IGT (if possible). 
  `build_example`: obligatory
  `with_primaryText`
  `with_language`
  `example_id`
  `format`
  `title`
  `comment`
  `source`
#}
{% import 'fmt_util.md' as util %}
{% if format=="subexample" %}
    {% set class_="subexample" %}
{% else %}
    {% set class_="example" %}
{% endif %}
{% set rich = data["examples"][ctx.id] %}
{% set counters = namespace(index = 0, offset=0) %}
{% set wordlist = [] %}
{% set morphlist = [] %}
{% for c in range(0,ctx.cldf.analyzedWord|length) %}
    {% set wordparts = [] %}
    {% set morphparts = [] %}
    {% if ctx.cldf.analyzedWord[c] is not none %}
        {% for part in ctx.cldf.analyzedWord[c].split("=")%}
            {% set position = counters.index + counters.offset %}
            {% if rich.multi_refs["exampleparts"]|length > position and rich.multi_refs["exampleparts"][position]["Index"]|int == c+counters.offset%}
                {% set _ = wordparts.append(util.link(rich.multi_refs["exampleparts"][position].wordform, html=True)) %}
                {% set _ = morphparts.append(util.render_form(rich.multi_refs["exampleparts"][position].wordform)) %}
            {% else %}
                {% set _ = wordparts.append(ctx.cldf.analyzedWord[c]) %}
                {% set _ = morphparts.append("&nbsp;") %}
                {% set counters.index = counters.index-1 %}
            {% endif %}
            {% set counters.offset = counters.offset + 1 %}
        {% endfor %}
    {% else %}
        {% set _ = wordparts.append("") %}    
    {% endif %}
    {% set counters.offset = counters.offset - 1 %}
    {% set counters.index = counters.index+1 %}
    {% set _ = wordlist.append("=".join(wordparts)) %}
    {% set _ = morphlist.append("=".join(morphparts)) %}
{% endfor %}
{% set ex_data=dict(
    obj=wordlist,
    obj2=morphlist,
    gls=ctx.cldf.gloss,
    ftr=ctx.cldf.translatedText,
    txt=util.link(rich, html=True),
    lng=ctx.related("languageReference").name,
    src=util.get_src_string(ctx, source),
    ex_id=example_id or ctx.cldf.id,
    title=title,
    comment=comment,
    show_language=with_language,
    source_position=src_pos,
    show_primary=with_primaryText,
    audio=get_audio(ctx.cldf.mediaReference)
    ) %}
<ol class="{{class_}}">
{{ util.render_example(class_, build_example(ex_data))}}
{% if class_=="example" %}
</ol>
{% endif %}
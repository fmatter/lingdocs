{% import 'fmt_util.md' as util %}
{% if ids is defined %}
    {% set gathered_examples = [] %}
    {% for id in ids.split(",") %}
        {% for example in ctx %}
            {% if example.id == id %}
                {% set _ = gathered_examples.append(example) %}
            {% endif %}
        {% endfor %}
    {% endfor %}
    {% set ex_data = [] %}
    {% for ctx in gathered_examples %}

{% set rich = data["examples"][ctx.id] %}
{% set counters = namespace(index = 0, offset=0) %}
{% set wordlist = [] %}
{% set morphlist = [] %}
{% for c in range(0,ctx.cldf.analyzedWord|length) %}
    {% set wordparts = [] %}
    {% set morphparts = [] %}
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
    {% set counters.offset = counters.offset - 1 %}
    {% set counters.index = counters.index+1 %}
    {% set _ = wordlist.append("=".join(wordparts)) %}
    {% set _ = morphlist.append("=".join(morphparts)) %}
{% endfor %}

        {% set _ = ex_data.append(dict(
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
            )) %}
    {% endfor %}
    {% set gathered_examples, full_preamble = build_examples(ex_data)%}
```{=html}
<ol class="example">
    <li class="example" id="{{example_id}}">
    <div class="preamble"> {{full_preamble}} </div>
        <ol class="subexample">
            {% for data in gathered_examples %}
                    {{ util.render_example("subexample", data) }}
            {% endfor %}
        </ol>
    </li>
</ol>
```
{% endif %}

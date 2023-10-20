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
        {% set _ = ex_data.append(dict(
            obj=ctx.cldf.analyzedWord,
            gls=ctx.cldf.gloss,
            ftr=ctx.cldf.translatedText,
            txt=ctx.cldf.primaryText,
            lng=ctx.related("languageReference").name,
            src=util.get_src_string(ctx, source),
            ex_id=ctx.cldf.id,
            title=title,
            comment=comment,
            show_language=with_language,
            source_position=src_pos,
            show_primary=with_primaryText
            )) %}
    {% endfor %}
    {% set gathered_examples, full_preamble = build_examples(ex_data)%}
::: {.ex formatGloss=true}
{{full_preamble}}
{% for data in gathered_examples %}
a.
{%if data["srf"]%}| {{data["srf"]}}
{%endif%}
| {%for x in data["obj"]%}{{x}} {%endfor%}

| {%for x in data["gls"]%}{{x}} {%endfor%}

| {{data["ftr"]}}
{% endfor %}
:::
{% endif %}

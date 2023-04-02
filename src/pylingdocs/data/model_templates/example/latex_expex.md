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
{% import 'pld_util.md' as util %}
{% if ctx.references %}
{% set ref_string = " " + util.references(ctx.references) %}
{% else %}
{% set ref_string = "" %}
{% endif %}
{%set corpus_string = ctx.data.get("Text_ID")%}
{% if corpus_string %}
{% set corpus_string = "[txt]("+corpus_string+")"%}
{%else%}
{%set corpus_string = ""%}
{%endif%}
{% set example_data = build_example(
    ctx.related('languageReference').name,
    sanitize_latex(ctx.cldf.primaryText),
    title,
    ref_string,
    show_language,
    corpus_string=corpus_string,
    custom_source=source,
    hide_primary=hide_primary) %}
```{=latex}
{% if format=="subexample" %}\a{%else%}\ex{%endif%} {% if example_data["title"] != "" %}{{ example_data["title"] }} \\{%endif%}
\label{% raw %}{{% endraw %}{{ example_id or ctx.id }}{% raw %}}{% endraw %}
{% if ctx.cldf.analyzedWord != [] %}
    \begingl{% if example_data["primary"] != "" %}
    \glpreamble {{ example_data["primary"] }} //{%endif%}
    {% set objlist = [] %}
    {% for o in ctx.cldf.analyzedWord %}
        {% set objlist = objlist.append(sanitize_latex(o)) %}
    {% endfor %}
    {% set glosslist = [] %}
    {% for g in ctx.cldf.gloss %}
        {% set glosslist = glosslist.append(sanitize_latex(decorate_gloss_string(g))) %}
    {% endfor %}
    \gla {{ " ".join(objlist) }}//
    \glb {{ " ".join(glosslist) }}//
    {% if ctx.cldf.translatedText != None %}
        \glft ‘{{ sanitize_latex(ctx.cldf.translatedText) }}’ \parentext{%raw%}{{%endraw%}{{example_data["source"]}}{%raw%}}{%endraw%}// {%else%}({{example_data["source"]}}){% endif %} 
    \endgl 
{% else %}
    \textit{% raw %}{{% endraw %}{{sanitize_latex(ctx.cldf.primaryText).strip()}} }\\
    {% if ctx.cldf.translatedText != None %}
        ‘{{ sanitize_latex(ctx.cldf.translatedText) }}’ {% endif %}
    {% endif %}
{% if format=="subexample" %}{%else%}\xe{%endif%}

```
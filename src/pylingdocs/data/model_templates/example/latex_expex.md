{# 
  Render an example object as IGT (if possible). 
  `with_primaryText`
  `with_internal_ref_link`
  `example_id`
  `format`
#}
{% import 'latex_util.md' as util %}
{% if ctx.references %}
{% set ref_string = " " + util.references(ctx.references) %}
{% else %}
{% set ref_string = "" %}
{% endif %}
```{=latex}
{% if format=="subexample" %}\a{%else%}\ex{%endif%} {{ ctx.related('languageReference').name }}{{ref_string}} \\
\label{% raw %}{{% endraw %}{{ example_id or ctx.id }}{% raw %}}{% endraw %}
{% if ctx.cldf.analyzedWord != [] %}
    \begingl
    \glpreamble {{ sanitize_latex(ctx.cldf.primaryText) }} //
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
        \glft ‘{{ sanitize_latex(ctx.cldf.translatedText) }}’// {% endif %} 
    \endgl 
{% else %}
    \textit{% raw %}{{% endraw %}{{sanitize_latex(ctx.cldf.primaryText).strip()}} }\\
    {% if ctx.cldf.translatedText != None %}
        ‘{{ sanitize_latex(ctx.cldf.translatedText) }}’ {% endif %}
    {% endif %}
{% if format=="subexample" %}{%else%}\xe{%endif%}

```
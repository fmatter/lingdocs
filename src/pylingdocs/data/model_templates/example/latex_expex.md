{# 
  Render an example object as IGT (if possible). 
  `with_primaryText`
  `with_internal_ref_link`
  `example_id`
#}
{% import 'util.md' as util %}
```{=latex}
\ex<{{ example_id or ctx.id }}> {{ ctx.related('languageReference').name }}{{ util.references(ctx.references, with_internal_ref_link=with_internal_ref_link) }} \\
\begingl
\glpreamble {{ sanitize_latex(ctx.cldf.primaryText) }} //
{% if ctx.cldf.analyzedWord != [] %}
{% set glosslist = [] %}
{% for w in ctx.cldf.gloss %}
    {% set glosslist = glosslist.append(sanitize_latex(w)) %}
{% endfor %}
\gla {{ " ".join(ctx.cldf.analyzedWord) }}//
\glb {{ " ".join(glosslist) }}//
{% endif %}
{% if ctx.cldf.translatedText != None %}
\glft ‘{{ sanitize_latex(ctx.cldf.translatedText) }}’// {% endif %} 
\endgl 
\xe
```
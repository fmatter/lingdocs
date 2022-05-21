{# 
  Render an example object as IGT (if possible). 
  `with_primaryText`
  `with_internal_ref_link`
  `example_id`
#}
{% import 'latex_util.md' as util %}
{% if ctx.references %}
{% set ref_string = " " + util.references(ctx.references) %}
{% else %}
{% set ref_string = "" %}
{% endif %}
```{=latex}
\ex {{ ctx.related('languageReference').name }}{{ref_string}} \\
\label{% raw %}{{% endraw %}{{ example_id or ctx.id }}{% raw %}}{% endraw %}\begingl
\glpreamble {{ sanitize_latex(ctx.cldf.primaryText) }} //
{% if ctx.cldf.analyzedWord != [] %}
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
{% endif %}
{% if ctx.cldf.translatedText != None %}
\glft ‘{{ sanitize_latex(ctx.cldf.translatedText) }}’// {% endif %} 
\endgl 
\xe
```
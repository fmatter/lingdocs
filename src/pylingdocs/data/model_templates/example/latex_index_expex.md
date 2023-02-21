{% import 'util.md' as util %}
{% if ids is defined %}
    {% set ids = ids.split(",") %}
    {% set gathered_examples = {} %}
        {% for example in ctx %}
            {% if example.id in ids %}
                {% set _ = gathered_examples.update({example.id: example}) %}
            {% endif %}
        {% endfor %}
```{=latex}
\pex\label{% raw %}{{% endraw %}{{example_id}}{% raw %}}{% endraw %}
{% for example_id, example in gathered_examples.items() %}
    \a {{ example.related('languageReference').name }}\\
    \label{% raw %}{{% endraw %}{{ example.id }}{% raw %}}{% endraw %}
    {% if example.cldf.analyzedWord != [] %}
        \begingl
        \glpreamble {{ sanitize_latex(example.cldf.primaryText) }} //
        {% set objlist = [] %}
        {% for o in example.cldf.analyzedWord %}
            {% set objlist = objlist.append(sanitize_latex(o)) %}
        {% endfor %}
        {% set glosslist = [] %}
        {% for w in example.cldf.gloss %}
            {% set glosslist = glosslist.append(sanitize_latex(     decorate_gloss_string(w))) %}
        {% endfor %}
        \gla {{ " ".join(objlist) }}//
        \glb {{ " ".join(glosslist) }}//
        {% if example.cldf.translatedText != None %}
            \glft ‘{{ example.cldf.translatedText }}’// {% endif %} 
        \endgl 
    {% else %}
        \textit{% raw %}{{% endraw %}{{sanitize_latex(example.cldf.primaryText).strip()}} }\\
        {% if example.cldf.translatedText != None %}
            ‘{{ sanitize_latex(example.cldf.translatedText) }}’ {% endif %}
        {% endif %}
{% endfor %}
\xe
```
{%else%}
no
{%endif%}



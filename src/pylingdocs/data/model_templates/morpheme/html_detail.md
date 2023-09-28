{% import "pylingdocs_util.md" as util %}
# {{ctx["Name"]}}

{% for k, v in ctx.items() %}
    {% if v %}
        {{k}}: {{v}}
    {% endif %}
{% endfor %}
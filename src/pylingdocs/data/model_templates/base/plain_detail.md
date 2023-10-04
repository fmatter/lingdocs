{% for k, v in ctx.items() %}
    {% if v %}
* {{k}}: {{v}}
    {% endif %}
{% endfor %}
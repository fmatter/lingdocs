{% for k, v in ctx.items() %}
{% if v is not none %}
- {{k}}: {{v}}
{% endif %}
{% endfor %}
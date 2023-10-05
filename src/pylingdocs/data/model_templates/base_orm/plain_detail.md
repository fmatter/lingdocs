{% for k, v in ctx.cldf.__dict__.items(): %}
{% if v is not none %}
- {{k}}: {{v}}
{% endif %}
{% endfor %}
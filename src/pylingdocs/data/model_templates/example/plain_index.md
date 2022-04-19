{% import 'util.md' as util %}
{% if ids is defined %}
{%set ids = ids.split(",")%}
{% for example in ctx %}
{% if example.id in ids %}
{{ example }}
{% endif %}
{% endfor %}
{%else%}
{%endif%}



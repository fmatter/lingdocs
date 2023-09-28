{% import 'util.md' as util %}
{% if ids is defined %}
    {%set ids = ids.split(",")%}
    {% set entities = [] %}
    {% for entity in ctx %}
        {% if entity.id in ids %}
            {% set entities = entities.append(entity["Name"]) %}
        {% endif %}
    {% endfor %}
{{ comma_and_list(entities)}}{%endif%}
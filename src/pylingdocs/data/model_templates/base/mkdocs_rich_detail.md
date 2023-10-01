{% import 'pld_util.md' as util %}

# {{util.label(ctx)}}

{% for key, val in ctx.fields.items() %}
    {% if (val is not none and val|string|length != 0)%}
* {{key}}: {{val}} 
    {% endif %}
{% endfor %}

{% for key, val in ctx.single_refs.items() %}
* {{key}}: {{util.link(val)}}
{% endfor %}

{% for key, values in ctx.multi_refs.items() %}
{% if values|length > 0 %}
    {% if key == "exampleparts" %}
## Examples
    {% else %}
## {{key}}
    {% endif %}
{% endif %}
{% for val in values %}
    {% if key == "exampleparts" %}
* {{util.link(val)}}
    {% else %}
* {{util.link(val)}}
    {% endif %}
{% endfor %}
{% endfor %}



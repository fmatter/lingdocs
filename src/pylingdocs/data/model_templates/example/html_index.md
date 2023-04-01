{% import 'html_util.md' as util %}
{% if ids is defined %}
    {% set ids = ids.split(",") %}
    {% set gathered_examples = {} %}
    {% for example in ctx %}
        {% if example.id in ids %}
            {% set _ = gathered_examples.update({example.id: example}) %}
        {% endif %}
    {% endfor %}
```{=html}
<ol class="example">
    <li class="example" id="{{example_id}}">
        <ol class="subexample">
            {% for example_id in ids %}
                {{ util.example(gathered_examples[example_id], class_="subexample") }}
            {% endfor %}
        </ol>
    </li>
</ol>
```
{% endif %}

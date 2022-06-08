{% import 'util.md' as util %}
{% if ids is defined %}
{%set ids = ids.split(",")%}
({{ example_id }}){% for example in ctx %}  
{% if example.id in ids %}
(a) {{ example.related('languageReference').name }} ({{ example.id }})  
{% if (example.cldf.analyzedWord == [] or with_primaryText) and example.cldf.primaryText != None %}{{ example.cldf.primaryText }}
{% endif %}
{% if example.cldf.analyzedWord != [] %}
{% set obj, gloss = pad_ex(example.cldf.analyzedWord, example.cldf.gloss) %}
{{ obj.replace(" ", "|WHITESPACE|") }}  
{{ gloss.replace(" ", "|WHITESPACE|") }}  
{% endif %}
{% if example.cldf.translatedText != None %}
‘{{ example.cldf.translatedText }}’{% endif %}  

{% endif %}
{% endfor %}
{%else%}
{%endif%}



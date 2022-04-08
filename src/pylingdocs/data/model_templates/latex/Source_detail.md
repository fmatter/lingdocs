{# 
  parencites=False
#}
{% import "util.md" as util %}
{% if parencites %}{% raw %}\parencite{{% endraw %}{{ctx.id}}{% raw %}}{% endraw %}
{% else %}
{% raw %}\textcites{{% endraw %}{{ctx.id}}{% raw %}}{% endraw %}
{% endif %}
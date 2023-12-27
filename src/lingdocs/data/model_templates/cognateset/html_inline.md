{% if inline %}
  <i>{{ ctx.data.get("Form", ctx.data.get("Name", ctx.data.get("Description", "Unnamed"))) }}</i>
{% else %}
  {% set vars = namespace(header=False) %}
  <table>
  {% for cog in ctx.cognates %}
  {% if cog.cldf.cognatesetReference == ctx.id %}
  {% if not vars.header %}
  <thead><tr><td>Form</td><td>Language</td><td>Alignment</td></tr></thead>
  <tbody>
  
  {% set vars.header = True %}
  {% endif %}
  <tr><td> _{{ cog.form.cldf.form }}_ </td><td> {{ cog.form.language.name }} </td><td><span class="alignment"> {{ " ".join(  cog.cldf.alignment) }} </span></td><td></tr>
  
  {% endif %}
  {% endfor %}
  </tbody>
  </table>
{%endif%}
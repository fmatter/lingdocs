{# 
  Render all sources of a dataset as bullet list. 
  Pass `with_anchor` to pre-pend an HTML anchor suitable as link target to each source.
  Pass `with_link` to append a markdown link if the source has DOI or URL.
#}
{% import 'util.md' as util %}
{% for src in ctx %}
- {{ util.source(src, with_anchor=False, with_link=with_link) }}
{% endfor %}
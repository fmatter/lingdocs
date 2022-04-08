{# 
  Render a source object as linearization according to the unified stylesheet for Linguistics.
  Pass `with_anchor` to pre-pend an HTML anchor suitable as link target.
  Pass `with_link` to append a markdown link if the source has DOI or URL.
  Pass `ref` to create a reference to the source object in "author(s) year" format.
  year_brackets=None, pages=True, with_internal_ref_link=False
#}
{% import "util.md" as util %}
{% set year_brackets = year_brackets or None %}
{% if ref is defined %}
{{ util.sourceref(ctx, year_brackets=year_brackets, with_internal_ref_link=False) }}{% else %}
{{ util.source(ctx, with_anchor=False, with_link=with_link) }}{% endif %}
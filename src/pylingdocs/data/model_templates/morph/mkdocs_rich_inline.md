{% import 'pylingdocs_util.md' as util%}
{% import 'pld_util.md' as butil%}
{% set rich = data["morphs"][ctx.id] %}
{{util.lfts(
    butil.link(rich),
    entity=ctx,
    translation=translation,
    source=source,
    with_language=with_language,
    with_source=with_source,
    with_translation=with_translation,
)}}
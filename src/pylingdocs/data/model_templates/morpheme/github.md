{% import 'pylingdocs_util.md' as util%}
{{util.lfts(
    "_"+ctx['Name']+"_",
    entity=ctx,
    translation=translation,
    source=source,
    with_language=with_language,
    with_source=with_source,
    with_translation=with_translation,
)}}
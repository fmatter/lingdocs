{% import 'pylingdocs_util.md' as util%}
{{util.lfts(
    "<i>" + ctx['Name'] + "</i>",
    entity=ctx,
    with_language=with_language or False,
    with_source=with_source or False,
    source_str=source_str,
    no_translation=no_translation,
    translation=translation
)}}
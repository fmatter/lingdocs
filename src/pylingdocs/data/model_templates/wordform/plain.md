{% import 'pylingdocs_util.md' as util%}
{{util.lfts(
    ctx.cldf.form,
    entity=ctx,
    with_language=with_language,
    with_source=with_source or False,
    translation=translation,
    no_translation=no_translation,
    source_str=source_str,
    mode="orm"
)}}
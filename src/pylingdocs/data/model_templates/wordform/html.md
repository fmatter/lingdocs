{% import 'pylingdocs_util.md' as util%}
{{util.lfts(
    "<i>" + ctx.cldf.form + "</i>",
    entity=ctx,
    with_language=with_language,
    with_source=with_source or False,
    translation=translation,
    no_translation=no_translation,
    source_str=source_str,
    mode="orm"
)}}
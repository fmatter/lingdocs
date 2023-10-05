{% import 'pld_util.md' as util%}
{{util.lfts(
    ctx.cldf.form,
    entity=ctx,
    translation=translation,
    source=source,
    with_language=with_language,
    with_source=with_source,
    with_translation=with_translation,
    mode="orm"
)}}
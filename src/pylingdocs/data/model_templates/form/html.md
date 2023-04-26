{% import 'pylingdocs_util.md' as util%}
{{util.lfts(
    "<i>" + ctx.cldf.form + "</i>",
    entity=ctx,
    translation=translation,
    source=source,
    with_language=with_language or lfts["show_lg"],
    with_source=with_source or lfts["show_src"],
    no_translation=no_translation or not lfts["show_ftr"],
    mode="orm"
)}}
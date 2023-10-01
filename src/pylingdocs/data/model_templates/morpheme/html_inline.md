{% import 'pylingdocs_util.md' as util%}
{{util.lfts(
    "<i>" + ctx.get("Name", ctx.get("Form", "?")) + "</i>",
    entity=ctx,
    translation=translation,
    source=source,
    with_language=with_language,
    with_source=with_source,
    with_translation=with_translation,
)}}
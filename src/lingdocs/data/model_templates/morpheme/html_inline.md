{% import 'pld_util.md' as pld_util%}
{% import 'fmt_util.md' as util%}
{{pld_util.lfts(
    "<i>" + util.get_label(ctx) + "</i>",
    entity=ctx,
    translation=translation,
    source=source,
    with_language=with_language,
    with_source=with_source,
    with_translation=with_translation,
)}}
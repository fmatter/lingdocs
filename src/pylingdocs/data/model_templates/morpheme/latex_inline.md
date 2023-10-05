{% import 'pld_util.md' as util%}
{{util.lfts(
    "\obj{"+ctx['Name']+"}",
    entity=ctx,
    translation=translation,
    source=source,
    with_language=with_language,
    with_source=with_source,
    with_translation=with_translation,
    citation_mode="biblatex"
)}}
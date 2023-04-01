{% import 'pylingdocs_util.md' as util%}
{{util.lfts(
    "\obj{"+ctx.cldf.form+"}",
    entity=ctx,
    with_language=with_language or False,
    with_source=with_source or False,
    source_str=source_str,
    translation=translation,
    no_translation=no_translation,
    mode="orm",
    citation_mode="biblatex"
)}}
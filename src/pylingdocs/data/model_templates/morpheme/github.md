{% import 'pylingdocs_util.md' as util%}
{{util.lfts(
    "_"+ctx['Name']+"_",
    entity=ctx,
    with_language=with_language or False,
    with_source=with_source or False,
    source_str=source_str,
    no_translation=no_translation,
    translation=translation,
    citation_mode="biblatex"
)}}
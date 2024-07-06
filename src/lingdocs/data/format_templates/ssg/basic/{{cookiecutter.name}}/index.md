{% if cookiecutter.conf.get("preamble") == "toml" %}+++
title = "{{ cookiecutter.project_title }}"
version = "{{ cookiecutter.version }}"
+++
{% endif %}
<link rel="stylesheet" href="/tables.css"/>
<link rel="stylesheet" href="/examples.css"/>
<link rel="stylesheet" href="/glossing.css"/>
<link rel="stylesheet" href="/alignment.css"/>
<link rel="stylesheet" href="/toc.css"/>
<script src="/examples.js"></script>
<script src="/glossing.js"></script>
<script src="/crossref.js"></script>
<script src="/alignment.js"></script>

{% if cookiecutter.conf.get("hypothes.is") %}<script src="https://hypothes.is/embed.js" async></script>{% endif %}

<article style="max-width: 80ch; text-align: justify;">
    <div class="version">v{{ cookiecutter.version }}</div>
    <div class="author">{{ cookiecutter.author }}</div>
    {% if cookiecutter.abstract %}<div class="abstract">
        <b>Abstract</b>
        <p>{{ cookiecutter.abstract }}</p>
    </div>
    {% endif %} {{ cookiecutter.content }}
    <script>{{cookiecutter.glossing_abbrevs}}</script>
</article>

<script>
    numberExamples();
    numberSections();
    numberCaptions();
    resolveCrossrefs();
</script>

<script>
    var alignments = document.getElementsByClassName("alignment");
    for (var i = 0, alignment; (alignment = alignments[i]); i++) {
        alignment.innerHTML = plotWord(alignment.innerHTML, "span");
    }
</script>

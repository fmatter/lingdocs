import itertools
import collections

from pycldf import Sources, Dataset
from clldutils.misc import nfilter
from clldutils.color import qualitative_colors
from clld.cliutil import Data, bibtex2source
from clld.db.meta import DBSession
from clldutils import jsonlib
from clld.db.models import common
from clld.lib import bibtex

import {{cookiecutter.clld_slug}}
from {{cookiecutter.clld_slug}} import models
from clld_morphology_plugin.models import Morpheme, Morph, Meaning

def main(args):
    data = Data()
    data.add(
        common.Dataset,
        {{cookiecutter.clld_slug}}.__name__,
        id={{cookiecutter.clld_slug}}.__name__,
        domain='{{cookiecutter.url}}',
        publisher_name="{{cookiecutter.publisher}}",
        publisher_place="{{cookiecutter.location}}",
        publisher_url="{{cookiecutter.location}}",
        license="http://creativecommons.org/licenses/by/4.0/",
        jsondata={
            'license_icon': 'cc-by.png',
            'license_name': 'Creative Commons Attribution 4.0 International License'},
    )

    cldfs = [Dataset.from_metadata(x) for x in {{cookiecutter.cldf_paths}}]

    {% if cookiecutter.single_cldf == True %}
    cldf = cldfs[0]
    contrib = data.add(
        common.Contribution,
        None,
        id='cldf',
        name=cldf.properties.get('dc:title'),
        description=cldf.properties.get('dc:bibliographicCitation'),
    )
    {% else %}
    contrib = data.add(
        common.Contribution,
        None,
        id="{{cookiecutter.clld_slug}}",
        name="{{cookiecutter.title}}",
        description="{{cookiecutter.citation}}",
    )
    {% endif %}

    for cldf in cldfs:
        for lang in cldf.iter_rows('LanguageTable'):
            data.add(
                common.Language,
                lang['ID'],
                id=lang['ID'],
                name=lang['Name'],
                latitude=lang['Latitude'],
                longitude=lang['Longitude'],
            )

        for morpheme in cldf.iter_rows('MorphsetTable'):
            data.add(
                Morpheme,
                morpheme['ID'],
                id=morpheme['ID'],
                name=morpheme['Form'],
                language=data["Language"][morpheme["Language_ID"]],
                meaning=morpheme["Parameter_ID"]
            )

        for morph in cldf.iter_rows('MorphTable'):
            data.add(
                Morph,
                morph['ID'],
                id=morph['ID'],
                name=morph['Form'],
                language=data["Language"][morph["Language_ID"]],
                morpheme=data["Morpheme"][morph["Morpheme_ID"]]
            )

        for ex in cldf.iter_rows("ExampleTable"):
            print(ex)
            data.add(common.Sentence,
            ex["ID"],
            id=ex["ID"],
            name=ex["Primary_Text"],
            description=ex["Translated_Text"],
            analyzed="\t".join(ex["Analyzed_Word"]),
            gloss="\t".join(ex["Gloss"]),
            language=data["Language"][ex["Language_ID"]],
            comment=ex["Comment"],
        )
    
        for rec in bibtex.Database.from_file(cldf.bibpath, lowercase=True):
            data.add(common.Source, rec.id, _obj=bibtex2source(rec))

#     refs = collections.defaultdict(list)


def prime_cache(args):
    """If data needs to be denormalized for lookup, do that here.
    This procedure should be separate from the db initialization, because
    it will have to be run periodically whenever data has been updated.
    """

from cookiecutter.main import cookiecutter
import configparser
from pybtex.database.input import bibtex
from pybtex.database import BibliographyData, Entry
import datetime
from clldutils import jsonlib

config = configparser.ConfigParser()
config.read("config.ini")


def get_citation(data):
    id = data.pop("id", "new_bibkey")
    if "year" not in data:
        date = datetime.date.today()
        data["year"] = date.strftime("%Y")

    bib_data = BibliographyData(
        {
            id: Entry("online", [(k, v) for k, v in data.items()]),
        }
    )
    return data["title"]
    return bib_data.to_string("bibtex")


extra = {}
for x in ["url", "title", "location", "author", "publisher"]:
    extra[x] = dict(config["metadata"]).get(x, "")
extra["clld_slug"] = dict(config["metadata"]).get("id", "new_clld_app")
extra["citation"] = get_citation(dict(config["metadata"]))
extra["abstract"] = open("abstract.txt", "r").read()

paths = config["cldf"]["cldf_paths"].split(" ")
jsonlib.dump(paths, "cldf_paths.json")
extra["single_cldf"] = len(paths) == 1

for k, v in dict(config["clld"]).items():
    extra[k] = v
cookiecutter(".", overwrite_if_exists=True, extra_context=extra, no_input=True)

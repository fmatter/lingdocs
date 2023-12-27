"""Various helpers"""
import logging

ORCID_STR = "https://orcid.org/"
log = logging.getLogger(__name__)

bibtex_repl = {"location": "address"}
bibtex_rev = {y: x for x, y in bibtex_repl.items()}


def _license_url(s):
    license_dic = {"CC-BY-SA-4.0": "http://creativecommons.org/licenses/by/4.0/"}
    return license_dic.get(s, "")


def _fill_repo(md):
    if "repository" in md:
        if "version" in md:
            md["url"] = md["repository"] + f"/tree/{md['version']}"
        elif "url" not in md:
            md["url"] = md["repository"]


# def _load_bib(metadata_file=METADATA_FILE):
#     md = _read_metadata_file(metadata_file)
#     entry_type = md.get("type", "article")
#     with open(DATA_DIR / "bibtex_schemes.json", "r", encoding="utf-8") as f:
#         bibschemes = json.loads(f.read())
#     if entry_type not in bibschemes:
#         log.error(
#             f"Don't know how to handle type '{entry_type}', defaulting to 'article'"
#         )
#         entry_type = "article"
#     good_fields = (
#         bibschemes[entry_type]["required"] + bibschemes[entry_type]["optional"]
#     )
#     good_fields = [bibtex_rev.get(x, x) for x in good_fields] + ["url"]
#     year = datetime.now().strftime("%Y")
#     date = datetime.now().strftime("%Y-%m-%d")
#     author_string = []
#     if "authors" in md:
#         for author in md["authors"]:
#             author_string.append(f'{author["family-names"]}, {author["given-names"]}')
#         bibkey = (
#             slugify(md["authors"][0]["family-names"])
#             + year
#             + slugify(md.pop("id", "new-lingdocs-project"))
#         )
#     else:
#         author_string.append("Anonymous")
#         bibkey = "anonymous" + year + slugify(md.pop("id", "new-lingdocs-project"))
#         md["authors"] = [{"family-names": "Anonymous", "given-names": "A."}]

#     md["title"] = md.get("title", "Put your title here.")
#     if "version" in md:
#         md["title"] += f' (version {md["version"]})'
#     else:
#         md["version"] = "0.0.0"
#     _fill_repo(md)
#     bibtex_fields = {
#         "author": " and ".join(author_string),
#         "year": year,
#         "urldate": date,
#     }
#     for field, value in md.items():
#         if field in good_fields:
#             bibtex_fields[field] = value
#     bib_data = BibliographyData(
#         {bibkey: Entry(entry_type, list(bibtex_fields.items()))}
#     )
#     return bib_data

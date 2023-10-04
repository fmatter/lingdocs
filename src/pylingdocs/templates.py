import logging

from writio import load

from pylingdocs.config import DATA_DIR, PLD_DIR
from pylingdocs.formats import builders

log = logging.getLogger(__name__)


def _fn(base, m, f, v, r):
    m = str(m).lower()
    f = str(f).lower()
    if r:
        return base / m / f"{f}_{v}_rich.md"
    return base / m / f"{f}_{v}.md"


def _parent_builder(builder):
    res = builder.__class__.__bases__[0]
    if res.name == "boilerplate":
        return None
    return res()


def _parent_model(model, base=False):
    res = model.__class__.__bases__[0]
    if res == object:
        return None
    if res.name in ["Base", "Base_ORM"] and not base:
        return None
    return res()


# order:
# pld model   builder
# pld pmodel    builder
# in  model   builder
# in  pmodel    builder

# pld model   pbuilder
# pld pmodel    pbuilder
# in  model   pbuilder
# in  pmodel    pbuilder

# pld model   gpbuilder
# pld pmodel    gpbuilder
# in  model   gpbuilder
# in  pmodel    gpbuilder

# pld gpmodel   builder
# in  gpmodel    builder
# pld gpmodel   pbuilder
# in  gpmodel    pbuilder

# pld base    builder
# in  base    builder
# pld base    pbuilder
# in  base    pbuilder


def _candidates(base, cbase, m, b):
    # print(f"\n\n\nYO: {m.name} and {b.name}")
    pb = _parent_builder(b)
    pm = _parent_model(m)

    for builder in [b, pb]:
        if not builder:
            continue
        # print("builder", builder.name)
        for basis in [cbase, base]:
            # print("base", basis)
            for model in [m, pm]:
                if not model:
                    continue
                # print("model", getattr(model, "name", "None"))
                yield (basis, model, builder)
    if pb:
        gpb = _parent_builder(pb)
        if gpb:
            for model in [m, pm]:
                if model:
                    yield (cbase, model, gpb)
    if pm:
        gpm = _parent_model(pm)
        if gpm:
            for x in _candidates(base, cbase, gpm, b):
                yield x
    final_baws = _parent_model(m, base=True)
    if final_baws:
        for x in _candidates(base, cbase, final_baws, b):
            yield x


def find_template(model, builder, view, rich=False):
    """Finds a template for a given model, a given output format, a given view; data-rich or not"""
    # log.debug(f"Searching template: {model.name}/{builder.label}_{view}")
    custom_base = PLD_DIR / "model_templates"
    base = DATA_DIR / "model_templates"

    # cands = []
    # for b, m, f in _candidates(base, custom_base, model, builder):
    #     cands.append({"Base": b.parents[0], "Model": m.name, "Format": f.label})
    # cands = pd.DataFrame(cands)
    # input(cands)

    for b, m, f in _candidates(base, custom_base, model, builder):
        path = _fn(base, m.name, f.label, view, rich)
        if path.is_file():
            return path
    log.warning(
        f"No template found for {model.name}/{builder.label}_{view} (last try {m.name}/{b.label})"
    )
    return None


name_dict = {
    "list": "index",
    "detail": "page",
    "inline": "detail",
    "index": "indexpage",
}


def load_templates(target_builders, models):
    templates = {}
    for fn in target_builders:
        f = builders[fn]
        templates[f.label] = {}
        for m in models:
            for view in ["inline", "list", "index", "detail"]:
                res = find_template(m, f, view)
                if res:
                    templates[f.label][f"{m.cldf_table}_{name_dict[view]}.md"] = load(
                        res
                    )
    return templates


# for k, v in TEMPLATES.items():
#     print(k)
#     for table, template in v.items():
#         print(f"    {table}: {template}")

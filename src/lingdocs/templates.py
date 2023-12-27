import logging

from writio import load

from lingdocs.config import DATA_DIR, PLD_DIR, config

log = logging.getLogger(__name__)
# log.setLevel(logging.DEBUG)


def _fn(base, m, f, v, r):
    m = str(m).lower()
    f = str(f).lower()
    if m == "example" and f == "latex":
        f = f"{f}_{config['latex']['interlinear']}"
    if r:
        rs = "_rich"
    else:
        rs = ""
    if r:
        return base / m / f"{f}_{v}{rs}.md"
    return base / m / f"{f}_{v}.md"


def _parent_builder(builder):
    res = builder.__class__.__bases__[0]
    if res == object or res.name == "boilerplate":
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
    # print(f"\n\ngetting cands for {m.name} and {b.name}")
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
            for x in _candidates(base, cbase, m, gpb):
                yield x
    if pm:
        gpm = _parent_model(pm)
        if gpm:
            for x in _candidates(base, cbase, gpm, b):
                yield x
    final_baws = _parent_model(m, base=True)
    if final_baws:
        for x in _candidates(base, cbase, final_baws, b):
            yield x


def find_template(model, builder, view, rich=config["data"]["rich"]):
    """Finds a template for a given model, a given output format, a given view; data-rich or not"""
    log.debug(f"Searching template: {model.name}/{builder.name}_{view}")
    custom_base = PLD_DIR / "model_templates"
    base = DATA_DIR / "model_templates"

    # import pandas as pd
    # cands = []
    # for b, m, f in _candidates(base, custom_base, model, builder):
    #     cands.append({"Base": b.parents[0], "Model": m.name, "Format": f.label})
    # cands = pd.DataFrame(cands)
    # input(cands.to_string())

    for b, m, f in _candidates(base, custom_base, model, builder):
        log.debug(f"{b}:{m}/{f}")
        path = _fn(b, m.name, f.name, view, r=rich)
        if path.is_file():
            log.debug(f"Using template {path} for {model.name}/{builder.name}_{view}")
            return path
    for b, m, f in _candidates(base, custom_base, model, builder):
        poor_path = _fn(b, m.name, f.name, view, r=not rich)
        if poor_path.is_file():
            log.debug(
                f"Using template {poor_path} for {model.name}/{builder.name}_{view}"
            )
            return poor_path
    log.warning(
        f"No template found for {model.name}/{builder.name}_{view} (last tries {path} and {poor_path})"
    )
    return None


name_dict = {
    "list": "index",
    "detail": "detail",
    "inline": "detail",
    "index": "index",
}


def load_templates(target_builder, models, rich=None):
    config.load_from_dir(".")
    rich = rich or config["data"]["rich"]
    # templates = {fn: {"text": {}, "data": {}} for fn in target_builders}
    templates = {"text": {}, "data": {}}
    f = target_builder
    # for fn in target_builders:
    # f = builders[fn]()
    for m in models:
        for view in ["inline", "list"]:
            res = find_template(m, f, view, rich=rich)
            if res:
                templates["text"][f"{m.cldf_table}_{name_dict[view]}.md"] = load(res)
        for view in ["index", "detail"]:
            res = find_template(m, f, view, rich=rich)
            if res:
                templates["data"][f"{m.cldf_table}_{name_dict[view]}.md"] = load(res)
    return templates


# for k, v in TEMPLATES.items():
#     print(k)
#     for table, template in v.items():
#         print(f"    {table}: {template}")

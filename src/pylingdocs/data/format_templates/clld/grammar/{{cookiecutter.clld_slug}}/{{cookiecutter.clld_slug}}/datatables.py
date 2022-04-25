from clld.web import datatables
from clld.web.datatables.base import Col
from clld.web.datatables.base import LinkCol
from clld.web.datatables.base import LinkToMapCol
from clld_morphology_plugin.datatables import includeme as tt
from sqlalchemy.orm import joinedload
from {{cookiecutter.clld_slug}} import models


def includeme(config):
    # config.register_datatable("meanings", Meanings)
    # config.register_datatable("morphs", Morphs)
    # config.register_datatable("morphemes", Morphemes)
    tt(config)
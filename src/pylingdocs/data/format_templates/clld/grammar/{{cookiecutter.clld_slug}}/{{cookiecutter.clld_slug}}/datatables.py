from sqlalchemy.orm import joinedload
from clld.web import datatables
from clld.web.datatables.base import LinkCol, Col, LinkToMapCol

from {{cookiecutter.clld_slug}} import models
from clld_morphology_plugin.datatables import includeme as tt

def includeme(config):
    # config.register_datatable("meanings", Meanings)
    # config.register_datatable("morphs", Morphs)
    # config.register_datatable("morphemes", Morphemes)
    tt(config)
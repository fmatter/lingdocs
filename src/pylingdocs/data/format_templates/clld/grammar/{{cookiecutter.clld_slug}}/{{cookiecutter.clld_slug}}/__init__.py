import collections
from clld.interfaces import IDomainElement
from clld.interfaces import IMapMarker
from clld.interfaces import IValue
from clld.interfaces import IValueSet
from clldutils.svg import data_url
from clldutils.svg import icon
from clldutils.svg import pie
from pyramid.config import Configurator
# we must make sure custom models are known at database initialization!
from {{cookiecutter.clld_slug}} import models


def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    config = Configurator(settings=settings)
    config.include('clld.web.app')
    config.include('clld_morphology_plugin')
    return config.make_wsgi_app()

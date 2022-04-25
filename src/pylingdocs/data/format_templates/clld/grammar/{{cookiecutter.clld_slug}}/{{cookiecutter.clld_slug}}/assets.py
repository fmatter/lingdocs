from pathlib import Path
import {{cookiecutter.clld_slug}}
from clld.web.assets import environment


environment.append_path(
    Path({{cookiecutter.clld_slug}}.__file__).parent.joinpath('static').as_posix(),
    url='/{{cookiecutter.clld_slug}}:static/')
environment.load_path = list(reversed(environment.load_path))

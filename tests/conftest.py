import pathlib
import pytest
from pycldf import Dataset


# try:
#     from importlib.resources import files  # pragma: no cover
# except ImportError:  # pragma: no cover
#     from importlib_resources import files  # pragma: no cover


@pytest.fixture(scope="module")
def data():
    return (
        pathlib.Path(__file__).parent / "data"
    )  # pathlib.Path(__file__).parent / "data"


@pytest.fixture
def md_path(data):
    return data / "cldf" / "metadata.json"


@pytest.fixture
def dataset(md_path):
    return Dataset.from_metadata(md_path)

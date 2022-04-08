import pathlib
import pytest
from pycldf import Dataset


DATA = pathlib.Path(__file__).parent / "data"


@pytest.fixture(scope="module")
def data():
    return DATA


@pytest.fixture
def md_path():
    return pathlib.Path(__file__).parent / "data" / "cldf" / "metadata.json"


@pytest.fixture
def dataset(md_path):
    return Dataset.from_metadata(md_path)

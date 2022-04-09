import pathlib
import pytest
from pycldf import Dataset
import logging

log = logging.getLogger(__name__)

@pytest.fixture(scope="module")
def data():
    return pathlib.Path(__file__).parent / "data"


@pytest.fixture
def md_path(data):
    return data / "cldf" / "metadata.json"


@pytest.fixture
def dataset(md_path):
    return Dataset.from_metadata(md_path)

from pylingdocs.helpers import _get_relative_file
from pathlib import Path


def test_structure():
    assert _get_relative_file(
        folder="my_own_contents", file="my_own_structure.yaml"
    ) == Path("my_own_contents/my_own_structure.yaml")
    assert _get_relative_file(
        folder="my_own_contents", file="path/my_own_structure.yaml"
    ) == Path("path/my_own_structure.yaml")

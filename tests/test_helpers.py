from pylingdocs.helpers import _get_relative_file, split_ref
from pathlib import Path


def test_structure():
    assert _get_relative_file(
        folder="my_own_contents", file="my_own_structure.yaml"
    ) == Path("my_own_contents/my_own_structure.yaml")
    assert _get_relative_file(
        folder="my_own_contents", file="path/my_own_structure.yaml"
    ) == Path("path/my_own_structure.yaml")

def test_refsplit():
    assert split_ref("anon1998grammar[301]") == ("anon1998grammar", "301")
    assert split_ref("anon1998grammar") == ("anon1998grammar", None)
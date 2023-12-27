from pathlib import Path
from lingdocs.helpers import _get_relative_file
from lingdocs.helpers import decorate_gloss_string
from lingdocs.helpers import load_content
from lingdocs.helpers import split_ref
from lingdocs.helpers import src
from lingdocs.helpers import write_file
from lingdocs.helpers import decorate_gloss_string


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


def test_gloss_decoration():
    test_cases = {
        "3P-kill-1SG": "|3||p|-kill-|1||sg|",
        "K. kill-REM": "K. kill-|rem|",
        "laugh[3SG.IMP]": "laugh[|3||sg|.|imp|]",
        "3>3-kill-IPFV.PST": "|3|>|3|-kill-|ipfv|.|pst|",
        "go-3SG.PST-1>2-CAUS[ERG]": "go-|3||sg|.|pst|-|1|>|2|-|caus|[|erg|]",
        "K.-ERG[3SG>2PL.PST]": "K.-|erg|[|3||sg|>|2||pl|.|pst|]",
        "M.SG": "|m|.|sg|",
        "test-3.PROG and-more-words": "test-|3|.|prog| and-more-words",
        "child\\PL": "child\\|pl|",
        "G14-child": "|g14|-child",
        "child(G14)": "child(|g14|)",
        "1>3": "|1|>|3|",
        "1S": "|1||s|",
        "3SG.F": "|3||sg|.|f|",
        "leave<PRS>-INF": "leave<|prs|>-|inf|",
        "3>F": "|3|>|f|",
        "F>3": "|f|>|3|",
        "1SG.PRO": "|1||sg|.|pro|",
        "P._A.": "P._A.",
    }
    for raw, expex in test_cases.items():
        assert decorate_gloss_string(raw, decoration=lambda x: f"|{x}|") == expex

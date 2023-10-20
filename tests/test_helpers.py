from pathlib import Path
from pylingdocs.helpers import _get_relative_file
from pylingdocs.helpers import decorate_gloss_string
from pylingdocs.helpers import load_content
from pylingdocs.helpers import split_ref
from pylingdocs.helpers import src
from pylingdocs.helpers import write_file, bump


def test_bump():
    assert bump("0.1.2") == "0.1.3"
    assert bump("0.1.2", step="minor") == "0.2.0"
    assert bump("0.1.2", step="major") == "1.0.0"


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
        "3P-kill-1SG": "\\gl{3}\\gl{p}-kill-\\gl{1}\\gl{sg}",
        "K. kill-REM": "K. kill-\\gl{rem}",
        "laugh[3SG.IMP]": "laugh[\\gl{3}\\gl{sg}.\\gl{imp}]",
        "3>3-kill-IPFV.PST": "\\gl{3}>\\gl{3}-kill-\\gl{ipfv}.\\gl{pst}",
        "go-3SG.PST-1>2-CAUS[ERG]": "go-\\gl{3}\\gl{sg}.\\gl{pst}-\\gl{1}>\\gl{2}-\\gl{caus}[\\gl{erg}]",
        "K.-ERG[3SG>2PL.PST]": "K.-\\gl{erg}[\\gl{3}\\gl{sg}>\\gl{2}\\gl{pl}.\\gl{pst}]",
        "M.SG": "\\gl{m}.\\gl{sg}",
        "test-3.PROG and-more-words": "test-\\gl{3}.\\gl{prog} and-more-words",
        "child\\PL": "child\\\\gl{pl}",
        "G14-child": "\\gl{g14}-child",
        "child(G14)": "child(\\gl{g14})",
        "1>3": "\\gl{1}>\\gl{3}",
        "1S": "\\gl{1}\\gl{s}",
        "3SG.F": "\\gl{3}\\gl{sg}.\\gl{f}",
        "leave<PRS>-INF": "leave<\\gl{prs}>-\\gl{inf}",
        "3>F": "\\gl{3}>\\gl{f}",
        "F>3": "\\gl{f}>\\gl{3}",
        "1SG.PRO": "\\gl{1}\\gl{sg}.\\gl{pro}",
    }
    for raw, expex in test_cases.items():
        assert decorate_gloss_string(raw) == expex

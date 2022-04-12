import io
import json
import logging
from panflute import Header
from panflute import Plain
from panflute import RawInline
from panflute import convert_text
from panflute import load
from panflute import run_filter


log = logging.getLogger(__name__)

section_types = ["section", "subsection", "subsubsection", "paragraph", "subparagraph"]


def reduce_header(elem, doc):
    del doc  # not used, but panflute insists on it...
    if isinstance(elem, Header):
        # log.debug(f"Removing header {elem.content}")
        cmd = f"\\{section_types[elem.level - 1]}{{"
        inlines = [RawInline(cmd, "tex")]
        inlines.extend(elem.content)
        inlines.append(RawInline("}", "tex"))
        return Plain(*inlines)
    return None


def fix_header(doc):
    file_handle = io.StringIO(doc)
    doc = load(file_handle)
    res = run_filter(reduce_header, doc=doc)
    res = convert_text(
        json.dumps(res.to_json()), output_format="latex", input_format="json"
    )
    return res

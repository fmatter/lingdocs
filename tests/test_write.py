from pylingdocs.helpers import write_content_file
import shutil


def test_write(data, dataset, caplog, monkeypatch, tmp_path):
    shutil.copytree(data / "content", tmp_path / "content")
    new_content = "a test"

    write_content_file(
        "intro",
        new_content,
        prefix_mode=None,
        source_dir=tmp_path / "content",
        structure_file=tmp_path / "content" / "structure.yaml",
    )

    with open(tmp_path / "content" / "intro.md", "r") as f:
        assert f.read() == new_content

from lingdocs.helpers import write_content_file
import shutil


def test_write(data, dataset, caplog, monkeypatch, tmp_path):
    shutil.copytree(data / "docs", tmp_path / "docs")
    new_content = "a test"

    write_content_file(
        "intro",
        new_content,
        prefix_mode=None,
        source_dir=tmp_path / "docs",
        structure_file=tmp_path / "docs" / "structure.yaml",
    )

    with open(tmp_path / "docs" / "intro.md", "r") as f:
        assert f.read() == new_content

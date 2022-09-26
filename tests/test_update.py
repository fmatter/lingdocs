import shutil
from pylingdocs.output import update_structure


def test_update(caplog, md_path, tmp_path, data, monkeypatch):

    shutil.copy(data / "metadata.yaml", tmp_path / "metadata.yaml")
    shutil.copytree(data / "content", tmp_path / "content")
    (tmp_path / "bench").mkdir()

    update_structure(
        content_dir=tmp_path / "content",
        bench_dir=tmp_path / "bench",
        structure_file=tmp_path / "content" / "structure.yaml",
        prefix_mode="alpha",
    )

    assert "Updating document " in caplog.text
    assert "F inalien" in caplog.text

    update_structure(
        content_dir=tmp_path / "content",
        bench_dir=tmp_path / "bench",
        structure_file=tmp_path / "content" / "structure.yaml",
        prefix_mode="numerical",
    )

    assert "6000 inalien" in caplog.text

from pathlib import Path


def test_default_config():
    from pylingdocs import config

    assert config.OUTPUT_DIR == Path("output")

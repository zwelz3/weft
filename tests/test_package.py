import tomllib
from pathlib import Path

import weft

ROOT = Path(__file__).resolve().parent.parent


def test_package_imports_and_has_version():
    assert weft.__version__ == "0.0.3"


def test_pytest_puts_src_on_path():
    # A bare checkout runs the suite without `pip install -e .`, so the
    # src layout must be on pytest's path or `import weft` fails at collection.
    config = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    assert "src" in config["tool"]["pytest"]["ini_options"]["pythonpath"]

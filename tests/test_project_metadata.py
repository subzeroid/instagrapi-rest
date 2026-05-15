import json
import tomllib
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]


def test_pyproject_replaces_requirements_txt():
    assert not (ROOT / "requirements.txt").exists()
    pyproject = tomllib.loads((ROOT / "pyproject.toml").read_text())
    deps = pyproject["project"]["dependencies"]
    assert "aiograpi==0.9.7" in deps
    assert pyproject["project"]["requires-python"] == ">=3.13"
    assert pyproject["project"]["name"] == "aiograpi-rest"
    assert pyproject["project"]["version"] == "1.0.1"
    assert pyproject["project"]["urls"]["Repository"] == "https://github.com/subzeroid/aiograpi-rest"


def test_dockerfile_uses_python_313_and_pyproject_install():
    dockerfile = (ROOT / "Dockerfile").read_text()
    assert "FROM python:3.13-slim" in dockerfile
    assert "requirements.txt" not in dockerfile
    assert "pip install" in dockerfile


def test_compose_runs_api_service_on_8000():
    compose = yaml.safe_load((ROOT / "docker-compose.yml").read_text())
    assert compose["name"] == "aiograpi-rest"
    api = compose["services"]["api"]
    assert api["build"] == "."
    assert "8000:8000" in api["ports"]


def test_app_manifest_uses_aiograpi_rest_identity():
    manifest = json.loads((ROOT / "app.json").read_text())
    assert manifest["name"] == "aiograpi-rest"
    assert manifest["repository"] == "https://github.com/subzeroid/aiograpi-rest"
    assert "aiograpi-rest" in manifest["keywords"]


def test_readme_documents_rename_reason():
    readme = (ROOT / "README.md").read_text()
    assert readme.startswith("# aiograpi-rest")
    assert "Renamed from `instagrapi-rest` to `aiograpi-rest` in v1.0.0" in readme
    assert "`aiograpi-rest` starts its own semver line at `1.0.0`" in readme
    assert "the service is now powered by `aiograpi`" in readme
    assert "docker run -d -p 8000:8000 subzeroid/aiograpi-rest" in readme

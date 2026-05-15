from pathlib import Path
import tomllib
import yaml


ROOT = Path(__file__).resolve().parents[1]


def test_pyproject_replaces_requirements_txt():
    assert not (ROOT / "requirements.txt").exists()
    pyproject = tomllib.loads((ROOT / "pyproject.toml").read_text())
    deps = pyproject["project"]["dependencies"]
    assert "aiograpi==0.9.7" in deps
    assert pyproject["project"]["requires-python"] == ">=3.13"


def test_dockerfile_uses_python_313_and_pyproject_install():
    dockerfile = (ROOT / "Dockerfile").read_text()
    assert "FROM python:3.13-slim" in dockerfile
    assert "requirements.txt" not in dockerfile
    assert "pip install" in dockerfile


def test_compose_runs_api_service_on_8000():
    compose = yaml.safe_load((ROOT / "docker-compose.yml").read_text())
    api = compose["services"]["api"]
    assert api["build"] == "."
    assert "8000:8000" in api["ports"]

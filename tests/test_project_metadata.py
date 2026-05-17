import json
import tomllib
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[1]


def test_pyproject_replaces_requirements_txt():
    assert not (ROOT / "requirements.txt").exists()
    pyproject = tomllib.loads((ROOT / "pyproject.toml").read_text())
    deps = pyproject["project"]["dependencies"]
    assert "aiograpi==0.9.7" in deps
    assert pyproject["project"]["requires-python"] == ">=3.13"
    assert pyproject["project"]["name"] == "aiograpi-rest"
    assert pyproject["project"]["version"] == "2.0.4"
    assert pyproject["project"]["urls"]["Repository"] == "https://github.com/subzeroid/aiograpi-rest"


def test_dockerfile_uses_python_313_and_pyproject_install():
    dockerfile = (ROOT / "Dockerfile").read_text()
    assert "FROM python:3.13-slim" in dockerfile
    assert "requirements.txt" not in dockerfile
    assert "pip install ." in dockerfile
    assert "pip install \".[test,docs]\"" in dockerfile
    assert "apt-get install" not in dockerfile
    assert "ffmpeg" not in dockerfile
    assert "gcc" not in dockerfile
    assert "ARG GIT_SHA=" in dockerfile
    assert "ARG BUILD_TIME=" in dockerfile
    assert "ENV GIT_SHA=${GIT_SHA}" in dockerfile
    assert "ENV BUILD_TIME=${BUILD_TIME}" in dockerfile
    assert "org.opencontainers.image.source=\"https://github.com/subzeroid/aiograpi-rest\"" in dockerfile
    assert "chown -R aiograpi:aiograpi /app" in dockerfile
    assert "USER aiograpi" in dockerfile
    assert "HEALTHCHECK" in dockerfile
    assert "http://127.0.0.1:8000/health" in dockerfile


def test_compose_runs_api_service_on_8000():
    compose = yaml.safe_load((ROOT / "docker-compose.yml").read_text())
    assert compose["name"] == "aiograpi-rest"
    api = compose["services"]["api"]
    assert api["build"] == {"context": ".", "target": "runtime"}
    assert "8000:8000" in api["ports"]
    test = compose["services"]["test"]
    assert test["build"] == {"context": ".", "target": "test"}
    assert test["profiles"] == ["test"]


def test_release_workflow_publishes_packages_images_and_artifacts():
    assert not (ROOT / ".github" / "workflows" / "docker.yml").exists()
    workflow = yaml.load((ROOT / ".github" / "workflows" / "release.yml").read_text(), Loader=yaml.BaseLoader)
    assert workflow["name"] == "Release"
    assert workflow["on"]["push"]["tags"] == ["[0-9]+.[0-9]+.[0-9]+", "v[0-9]+.[0-9]+.[0-9]+"]
    assert workflow["env"]["DOCKERHUB_IMAGE"] == "subzeroid/aiograpi-rest"
    assert workflow["env"]["GHCR_IMAGE"] == "ghcr.io/subzeroid/aiograpi-rest"
    assert workflow["jobs"]["publish"]["permissions"] == {
        "contents": "write",
        "id-token": "write",
        "packages": "write",
    }

    steps = workflow["jobs"]["publish"]["steps"]
    run_commands = "\n".join(step.get("run", "") for step in steps)
    assert "ruff check ." in run_commands
    assert "python scripts/generate_aiograpi_coverage.py --check" in run_commands
    assert "pytest --cov=. --cov-report=term-missing --cov-fail-under=100" in run_commands
    assert "mkdocs build --strict" in run_commands
    assert "python scripts/export_openapi.py release/openapi.json" in run_commands
    assert "python -m build" in run_commands

    dockerhub_login = next(step for step in steps if step.get("name") == "Log in to Docker Hub")
    assert dockerhub_login["uses"] == "docker/login-action@v3"
    assert dockerhub_login["with"]["username"] == "subzeroid"

    ghcr_login = next(step for step in steps if step.get("name") == "Log in to GitHub Container Registry")
    assert ghcr_login["uses"] == "docker/login-action@v3"
    assert ghcr_login["with"]["registry"] == "ghcr.io"

    assert any(step.get("uses") == "docker/build-push-action@v6" for step in steps)

    metadata_step = next(step for step in steps if step.get("uses") == "docker/metadata-action@v5")
    assert "${{ env.DOCKERHUB_IMAGE }}" in metadata_step["with"]["images"]
    assert "${{ env.GHCR_IMAGE }}" in metadata_step["with"]["images"]

    build_step = next(step for step in steps if step.get("uses") == "docker/build-push-action@v6")
    assert build_step["with"]["target"] == "runtime"
    assert build_step["with"]["platforms"] == "linux/amd64,linux/arm64"
    assert build_step["with"]["push"] == "true"
    assert build_step["with"]["provenance"] == "false"
    assert "GIT_SHA=${{ github.sha }}" in build_step["with"]["build-args"]
    assert "BUILD_TIME=${{ steps.build_time.outputs.value }}" in build_step["with"]["build-args"]

    pypi_step = next(step for step in steps if step.get("uses") == "pypa/gh-action-pypi-publish@release/v1")
    assert "with" not in pypi_step

    release_step = next(step for step in steps if step.get("uses") == "softprops/action-gh-release@v2")
    assert "release/openapi.json" in release_step["with"]["files"]
    assert "dist/*.whl" in release_step["with"]["files"]
    assert "dist/*.tar.gz" in release_step["with"]["files"]


def test_export_openapi_script_writes_artifact(tmp_path):
    from scripts import export_openapi

    output = export_openapi.export_openapi(tmp_path / "nested" / "openapi.json")

    data = json.loads(output.read_text())
    assert data["info"]["title"] == "aiograpi-rest"
    assert data["info"]["version"] == "2.0.4"


def test_export_openapi_main_writes_artifact(tmp_path):
    from scripts import export_openapi

    output = tmp_path / "openapi.json"
    export_openapi.main([str(output)])

    assert json.loads(output.read_text())["info"]["version"] == "2.0.4"


def test_export_openapi_script_requires_output_argument():
    from scripts import export_openapi

    with pytest.raises(SystemExit, match="Usage: export_openapi.py OUTPUT"):
        export_openapi.main([])


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
    assert "docker run -p 8000:8000 ghcr.io/subzeroid/aiograpi-rest" in readme
    assert "PyPI and GitHub Release artifacts are published from the same tag workflow" in readme


def test_github_docs_are_configured():
    pyproject = tomllib.loads((ROOT / "pyproject.toml").read_text())
    assert "mkdocs-material>=9.6,<10" in pyproject["project"]["optional-dependencies"]["docs"]

    mkdocs = yaml.safe_load((ROOT / "mkdocs.yml").read_text())
    assert mkdocs["site_name"] == "aiograpi-rest Documentation"
    assert mkdocs["repo_name"] == "subzeroid/aiograpi-rest"
    assert "aiograpi-coverage.md" in str(mkdocs["nav"])

    docs_workflow = (ROOT / ".github" / "workflows" / "docs.yml").read_text()
    assert "python scripts/generate_aiograpi_coverage.py --check" in docs_workflow
    assert "mkdocs build --strict" in docs_workflow
    assert "mkdocs gh-deploy --force" in docs_workflow

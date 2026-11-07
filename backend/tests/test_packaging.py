import importlib.util
import subprocess
from pathlib import Path
from zipfile import ZipFile

import pytest

HELPER = (
    Path(__file__).resolve().parents[2]
    / ".github"
    / "scripts"
    / "package_backend.py"
)


def load_packager():
    assert HELPER.is_file(), "The backend packaging helper must exist"
    spec = importlib.util.spec_from_file_location("package_backend", HELPER)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.create_package


@pytest.fixture
def source_tree(tmp_path):
    repository = tmp_path / "repository"
    backend = repository / "backend"
    (backend / "tests").mkdir(parents=True)
    (backend / "app").mkdir(parents=True)
    (backend / ".venv").mkdir()
    
    (backend / "app" / "__init__.py").touch()
    (backend / "app" / "main.py").write_text("# Version selected for deployment\n")
    (backend / "requirements.txt").write_text("fastapi\n")
    (backend / "tests" / "test_main.py").write_text("# Test code\n")
    (backend / ".env").write_text("LOCAL_ONLY=yes\n")
    (backend / ".venv" / "local.txt").write_text("Local environment\n")
    (backend / "untracked.py").write_text("# Untracked working copy\n")

    def git(*arguments):
        return subprocess.check_output(
            ["git", "-C", str(repository), *arguments], text=True
        ).strip()

    git("init", "--quiet")
    git("add", "backend/app", "backend/requirements.txt", "backend/tests")
    revision = git("write-tree")
    (backend / "app" / "main.py").write_text("# Later uncommitted changes\n")
    return repository, revision


def test_package_uses_selected_source_and_tested_dependency_versions(source_tree, tmp_path):
    create_package = load_packager()
    repository, revision = source_tree
    output = tmp_path / "backend.zip"
    requirements = "fastapi==0.162.0\nuvicorn==0.54.0\n"

    create_package(repository, revision, output, requirements)

    with ZipFile(output) as package:
        assert package.read("app/main.py") == b"# Version selected for deployment\n"
        assert package.read("requirements.txt").decode() == requirements
        assert "app/__init__.py" in package.namelist()
        assert "app/main.py" in package.namelist()
        assert "requirements.txt" in package.namelist()


def test_package_works_when_called_from_backend_directory(source_tree, tmp_path, monkeypatch):
    create_package = load_packager()
    repository, revision = source_tree
    monkeypatch.chdir(repository / "backend")
    output = tmp_path / "backend.zip"

    create_package(repository, revision, output, "fastapi==0.162.0\n")

    with ZipFile(output) as package:
        assert "app/main.py" in package.namelist()


def test_invalid_revision_does_not_create_deployment_archive(source_tree, tmp_path):
    create_package = load_packager()
    repository, _ = source_tree
    output = tmp_path / "backend.zip"

    with pytest.raises(subprocess.CalledProcessError):
        create_package(repository, "missing-revision", output, "fastapi==0.162.0\n")

    assert not output.exists()
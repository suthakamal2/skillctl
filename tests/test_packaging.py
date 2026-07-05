"""Smoke test for the build artefacts: sdist + wheel, console-script entry point."""

from __future__ import annotations

import shutil
import subprocess
import sys
import zipfile
from pathlib import Path

import pytest

PACKAGE_ROOT = Path(__file__).resolve().parent.parent


def _build_available() -> bool:
    try:
        import build  # noqa: F401
        return True
    except ImportError:
        return False


@pytest.mark.skipif(not _build_available(), reason="`build` not installed")
def test_build_produces_sdist_and_wheel(tmp_path: Path) -> None:
    """`python -m build` should emit one .tar.gz and one .whl under dist/."""
    work = tmp_path / "skillctl-build"
    shutil.copytree(PACKAGE_ROOT, work, ignore=shutil.ignore_patterns(
        "dist", "build", "*.egg-info", "__pycache__", ".pytest_cache",
    ))

    result = subprocess.run(
        [sys.executable, "-m", "build"],
        cwd=work,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, f"build failed:\nstdout: {result.stdout}\nstderr: {result.stderr}"

    dist = work / "dist"
    sdists = list(dist.glob("*.tar.gz"))
    wheels = list(dist.glob("*.whl"))
    assert len(sdists) == 1, f"expected 1 sdist, found {sdists}"
    assert len(wheels) == 1, f"expected 1 wheel, found {wheels}"


@pytest.mark.skipif(not _build_available(), reason="`build` not installed")
def test_wheel_contains_console_script_entry_point(tmp_path: Path) -> None:
    """The `skillctl` console script must be declared in the wheel's entry-points."""
    work = tmp_path / "skillctl-build"
    shutil.copytree(PACKAGE_ROOT, work, ignore=shutil.ignore_patterns(
        "dist", "build", "*.egg-info", "__pycache__", ".pytest_cache",
    ))

    subprocess.run(
        [sys.executable, "-m", "build", "--wheel"],
        cwd=work,
        check=True,
        capture_output=True,
        text=True,
    )

    wheel = next((work / "dist").glob("*.whl"))
    with zipfile.ZipFile(wheel) as z:
        entry_points = next(
            (n for n in z.namelist() if n.endswith("entry_points.txt")), None
        )
        assert entry_points, "wheel is missing entry_points.txt"
        content = z.read(entry_points).decode()
        assert "[console_scripts]" in content
        assert "skillctl = skillctl._cli:main" in content


def test_pyproject_version_matches_init() -> None:
    """The version declared in pyproject.toml must match skillctl.__version__."""
    import tomllib
    pyproject = tomllib.loads((PACKAGE_ROOT / "pyproject.toml").read_text())
    declared = pyproject["project"]["version"]

    from skillctl import __version__
    assert declared == __version__, (
        f"pyproject.toml version ({declared}) != skillctl.__version__ ({__version__})"
    )

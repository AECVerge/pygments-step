"""Developer tasks for pygments-step.

Sessions:
  bump     -- bump the version across ``pyproject.toml`` and
              ``pygments_step/__init__.py``.
  release  -- push ``main``, create an annotated ``vX.Y.Z`` tag on ``HEAD``,
              then push the tag, which triggers the ``release`` workflow
              (tests + publish to PyPI via OIDC Trusted Publishing).

Both sessions run on the current interpreter (no virtualenv) because they only
edit files and call ``git``; neither needs the package installed. Run them with
``nox`` (or ``pyp -m nox`` if installed), e.g.::

    nox -s bump -- 0.2.0
    nox -s release -- 0.2.0
"""

from __future__ import annotations

import pathlib
import re
import subprocess

import nox

ROOT = pathlib.Path(__file__).parent


def _run_git(*args: str) -> None:
    subprocess.run(["git", *args], check=True, cwd=str(ROOT))


def _current_version() -> str:
    text = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
    match = re.search(r'^version\s*=\s*"([^"]+)"', text, re.MULTILINE)
    if not match:
        raise SystemExit("Could not find the [project] version in pyproject.toml.")
    return match.group(1)


@nox.session(python=False)
def bump(session: nox.Session) -> None:
    """Bump the version in pyproject.toml and pygments_step/__init__.py."""
    if not session.posargs:
        session.error("usage: nox -s bump -- <new-version>")
        return
    new_version = session.posargs[0].lstrip("v")
    old_version = _current_version()

    targets = [
        (ROOT / "pyproject.toml", r'^version\s*=\s*"[^"]+"', f'version = "{new_version}"'),
        (ROOT / "pygments_step" / "__init__.py", r'__version__\s*=\s*"[^"]+"',
         f'__version__ = "{new_version}"'),
    ]

    for path, pattern, replacement in targets:
        text = path.read_text(encoding="utf-8")
        updated, count = re.subn(pattern, replacement, text, count=1, flags=re.MULTILINE)
        if count != 1:
            session.error(
                f"Could not update the version in {path.relative_to(ROOT)}."
            )
        path.write_text(updated, encoding="utf-8")
        session.log(f"Updated {path.relative_to(ROOT)} -> {new_version}")

    session.log(f"Bumped {old_version} -> {new_version}.")
    session.log(
        "Remember to add a CHANGELOG entry under a new '## [<version>] - <date>' "
        "section."
    )


@nox.session(python=False)
def release(session: nox.Session) -> None:
    """Push main, tag HEAD, then push the tag to trigger the release workflow."""
    if not session.posargs:
        session.error("usage: nox -s release -- <version>")
        return
    tag = "v" + session.posargs[0].lstrip("v")

    session.log("Pushing main so the release commit is on GitHub ...")
    _run_git("push", "origin", "main")

    session.log(f"Creating annotated tag {tag} ...")
    _run_git("tag", "-a", tag, "-m", f"pygments-step {tag}")

    session.log(f"Pushing {tag} (triggers the release workflow) ...")
    _run_git("push", "origin", tag)

    session.log("Done. Check the GitHub Actions tab for the release run.")

"""Developer tasks for pygments-step.

Sessions:
  bump     -- bump the version across ``pyproject.toml`` and
              ``pygments_step/__init__.py``.
  release  -- push ``main``, create an annotated ``vX.Y.Z`` tag on ``HEAD``,
              then push the tag, which triggers the ``release`` workflow
              (tests + publish to PyPI via OIDC Trusted Publishing).

Both sessions run on the current interpreter (no virtualenv) because they only
edit files and call ``git``; neither needs the package installed. Run them with
``nox``::

    nox -s bump -- 0.2.0
    nox -s release -- 0.2.0
"""

from __future__ import annotations

import pathlib
import re
import subprocess

import nox

ROOT = pathlib.Path(__file__).parent


def _git_out(*args: str) -> str:
    """Run a git command and return its trimmed stdout."""
    proc = subprocess.run(
        ["git", *args], check=True, cwd=str(ROOT),
        capture_output=True, text=True,
    )
    return proc.stdout.strip()


def _run_git(*args: str) -> None:
    """Run a git command, streaming output and raising on failure."""
    subprocess.run(["git", *args], check=True, cwd=str(ROOT))


def _tag_exists(tag: str) -> bool:
    proc = subprocess.run(
        ["git", "rev-parse", "-q", "--verify", f"refs/tags/{tag}"],
        cwd=str(ROOT), capture_output=True,
    )
    return proc.returncode == 0


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
    new_version = session.posargs[0].lstrip("v")
    tag = "v" + new_version

    # --- safety checks ---------------------------------------------------
    branch = _git_out("rev-parse", "--abbrev-ref", "HEAD")
    if branch != "main":
        session.error(
            f"You are on '{branch}', not 'main'. Check out main and pull the "
            "release commit before releasing."
        )

    dirty = _git_out("status", "--porcelain")
    if dirty:
        session.error(
            "The working tree has uncommitted changes. Commit them (and add the "
            "CHANGELOG entry) before creating the release tag."
        )

    version_in_project = _current_version()
    if version_in_project != new_version:
        session.error(
            f"pyproject.toml is at version {version_in_project}, but you asked "
            f"to release {new_version}. Run 'nox -s bump -- {new_version}' (and "
            "commit it) first."
        )

    _run_git("fetch", "origin", "main")
    behind = _git_out("rev-list", "--count", "main..origin/main")
    if behind != "0":
        session.error(
            f"Your local main is {behind} commit(s) behind origin/main. Run "
            "'git pull' before releasing."
        )

    if _tag_exists(tag):
        session.error(f"The tag {tag} already exists locally.")

    # --- the actual release ---------------------------------------------
    session.log("Pushing main so the release commit is on GitHub ...")
    _run_git("push", "origin", "main")

    session.log(f"Creating annotated tag {tag} ...")
    _run_git("tag", "-a", tag, "-m", f"pygments-step {tag}")

    session.log(f"Pushing {tag} (triggers the release workflow) ...")
    _run_git("push", "origin", tag)

    session.log("Done. Check the GitHub Actions tab for the release run.")

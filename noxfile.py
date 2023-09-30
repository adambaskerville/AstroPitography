from __future__ import annotations

import argparse
import shutil
from pathlib import Path

import nox

DIR = Path(__file__).parent.resolve()

nox.options.sessions = ["formatting", "linting", "typing", "testing"]

FORMATTING_TOOLS = (
    "black==23.3.0",
    "ruff==0.0.263",
)  
RUFF_FORMATTING_RULESET = "I"

LINT_SOURCE_PATHS = (
    "src/",
    "tests/",
    "noxfile.py",
)

ISORT_SOURCE_PATHS = (
    *LINT_SOURCE_PATHS,
    "docs/source/conf.py",
)

@nox.session(python=False)
def formatting(session: nox.Session) -> None:
    """
    Checks your code is formatted correctly (does not make changes).
    """
    session.install(*FORMATTING_TOOLS)
    session.run("black", "--preview", "--check", "--diff", ".")
    # fmt:off
    session.run("ruff", "check",
                "--select", RUFF_FORMATTING_RULESET,
                *ISORT_SOURCE_PATHS)
    # fmt:on

@nox.session(python=False)
def linting(session: nox.Session) -> None:
    """Run static code analysis and checks format is correct."""
    session.run("black", "--version", external=True)
    session.run("ruff", "--version", external=True)
    session.run("mypy", "--version", external=True)

    files = ["fuzzylite/", "tests/", "noxfile.py"]

    session.run("black", "--check", *files, external=True)
    session.run("ruff", "check", *files, external=True)
    session.run(
        "mypy",
        *files,
        external=True,
    )

@nox.session(python=False)
def typing(session: nox.Session) -> None:
    """
    Runs mypy typing check
    """
    session.run("mypy")

@nox.session(python=False)
def testing(session: nox.Session) -> None:
    """Run the tests in the project."""
    session.run(
        "coverage",
        "run",
        "-m",
        "pytest",
        external=True,
    )
    session.run(
        "coverage",
        "report",
        external=True,
    )

@nox.session
def test_publish(session: nox.Session) -> None:
    """Build the distributable and upload it to testpypi."""
    session.run("rm", "-rf", "dist/", external=True)
    session.run("poetry", "build", external=True)
    session.run("twine", "check", "--strict", "dist/*", external=True)
    session.run(
        "twine",
        "upload",
        "--repository",
        "testpypi",
        "dist/*",
        "--config-file",
        ".pypirc",
        "--verbose",
        external=True,
    )

@nox.session(reuse_venv=True)
def docs(session: nox.Session) -> None:
    """
    Build the docs. Pass "--serve" to serve. Pass "-b linkcheck" to check links.
    """

    parser = argparse.ArgumentParser()
    parser.add_argument("--serve", action="store_true", help="Serve after building")
    parser.add_argument(
        "-b", dest="builder", default="html", help="Build target (default: html)"
    )
    args, posargs = parser.parse_known_args(session.posargs)

    if args.builder != "html" and args.serve:
        session.error("Must not specify non-HTML builder with --serve")

    extra_installs = ["sphinx-autobuild"] if args.serve else []

    session.install("-e.[docs]", *extra_installs)
    session.chdir("docs")

    if args.builder == "linkcheck":
        session.run(
            "sphinx-build", "-b", "linkcheck", ".", "_build/linkcheck", *posargs
        )
        return

    shared_args = (
        "-n",  # nitpicky mode
        "-T",  # full tracebacks
        f"-b={args.builder}",
        ".",
        f"_build/{args.builder}",
        *posargs,
    )

    if args.serve:
        session.run("sphinx-autobuild", *shared_args)
    else:
        session.run("sphinx-build", "--keep-going", *shared_args)


@nox.session
def build_api_docs(session: nox.Session) -> None:
    """
    Build (regenerate) API docs.
    """

    session.install("sphinx")
    session.chdir("docs")
    session.run(
        "sphinx-apidoc",
        "-o",
        "api/",
        "--module-first",
        "--no-toc",
        "--force",
        "../src/{{ cookiecutter.project_name | lower | replace('-', '_') | replace('.', '_') }}",
    )

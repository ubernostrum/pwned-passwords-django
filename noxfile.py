"""
Automated testing via nox (https://nox.thea.codes/).

Combined with a working installation of nox (``pip install nox``), this file specifies a
matrix of tests, linters, and other quality checks which can be run individually or as a
suite.

To see available tasks, run ``nox --list``. To run all available tasks -- which requires
functioning installs of all supported Python versions -- run ``nox``. To run a single
task, use ``nox -s`` with the name of that task.

"""
import os

import nox

nox.options.default_venv_backend = "venv"
nox.options.reuse_existing_virtualenvs = True


# Tasks which run the package's test suites.
# -----------------------------------------------------------------------------------


@nox.session(tags=["tests"])
@nox.parametrize(
    "python,django",
    [
        # Python/Django testing matrix. Tests Django 3.2, 4.0, 4.1, on Python 3.7
        # through 3.11, skipping unsupported combinations: Django 3.2 and 4.0 do not
        # support Python 3.11, and Django 4.0 and 4.1 do not support Python 3.7.
        (python, django)
        for python in ["3.7", "3.8", "3.9", "3.10", "3.11"]
        for django in ["3.2", "4.0", "4.1"]
        if (python, django)
        not in [("3.7", "4.0"), ("3.7", "4.1"), ("3.11", "3.2"), ("3.11", "4.0")]
    ],
)
def tests_with_coverage(session: nox.Session, django: str) -> None:
    """
    Run the package's unit tests, with coverage report.

    """
    session.install("coverage[toml]", f"Django~={django}.0", ".")
    python_version = session.run(
        f"{session.bin}/python{session.python}", "--version", silent=True
    ).strip()
    django_version = session.run(
        f"{session.bin}/python{session.python}",
        "-Im",
        "django",
        "--version",
        silent=True,
    ).strip()
    session.log(f"Running tests with {python_version}/Django {django_version}")
    session.run(f"{session.bin}/python{session.python}", "-Im", "coverage", "--version")
    session.run(
        f"{session.bin}/python{session.python}",
        "-Wonce::DeprecationWarning",
        "-Im",
        "coverage",
        "run",
        "--source",
        "pwned_passwords_django",
        "runtests.py",
    )
    session.run(
        f"{session.bin}/python{session.python}", "-Im", "coverage", "report", "-m"
    )


# Tasks which test the package's documentation.
# -----------------------------------------------------------------------------------


@nox.session(python=["3.11"], tags=["docs"])
def docs_build(session: nox.Session) -> None:
    """
    Build the package's documentation as HTML.

    """
    session.install(
        "furo", "sphinx", "sphinx-notfound-page", "sphinxext-opengraph", "."
    )
    tempdir = session.create_tmp()
    session.chdir("docs")
    session.run(
        f"{session.bin}/python{session.python}",
        "-Im",
        "sphinx",
        "-b",
        "html",
        "-d",
        f"{tempdir}/doctrees",
        ".",
        f"{tempdir}/html",
    )


@nox.session(python=["3.11"], tags=["docs"])
def docs_docstrings(session: nox.Session) -> None:
    """
    Enforce the presence of docstrings on all modules, classes, functions, and
    methods.

    """
    session.install("interrogate")
    session.run(
        f"{session.bin}/python{session.python}", "-Im", "interrogate", "--version"
    )
    session.run(
        f"{session.bin}/python{session.python}",
        "-Im",
        "interrogate",
        "-v",
        "src/",
        "tests/",
        "noxfile.py",
    )


@nox.session(python=["3.11"], tags=["docs"])
def docs_spellcheck(session: nox.Session) -> None:
    """
    Spell-check the package's documentation.

    """
    session.install(
        "furo",
        "pyenchant",
        "sphinx",
        "sphinxcontrib-spelling",
        "sphinx-notfound-page",
        "sphinxext-opengraph",
        ".",
    )
    tempdir = session.create_tmp()
    session.chdir("docs")
    session.run(
        f"{session.bin}/python{session.python}",
        "-Im",
        "sphinx",
        "-W",  # Promote warnings to errors, so that misspelled words fail the build.
        "-b",
        "spelling",
        "-d",
        f"{tempdir}/doctrees",
        ".",
        f"{tempdir}/html",
        # On Apple Silicon Macs, this environment variable needs to be set so
        # pyenchant can find the "enchant" C library. See
        # https://github.com/pyenchant/pyenchant/issues/265#issuecomment-1126415843
        env={"PYENCHANT_LIBRARY_PATH": os.getenv("PYENCHANT_LIBRARY_PATH", "")},
    )


# Code formatting checks.
#
# These checks do *not* reformat code -- that happens in pre-commit hooks -- but will
# fail a CI build if they find any code that needs reformatting.
# -----------------------------------------------------------------------------------


@nox.session(python=["3.11"], tags=["formatters"])
def format_black(session: nox.Session) -> None:
    """
    Check code formatting with Black.

    """
    session.install("black")
    session.run(f"{session.bin}/python{session.python}", "-Im", "black", "--version")
    session.run(
        f"{session.bin}/python{session.python}",
        "-Im",
        "black",
        "--check",
        "--diff",
        "src/",
        "tests/",
        "docs/",
        "noxfile.py",
    )


@nox.session(python=["3.11"], tags=["formatters"])
def format_isort(session: nox.Session) -> None:
    """
    Check code formating with Black.

    """
    session.install("isort")
    session.run(f"{session.bin}/python{session.python}", "-Im", "isort", "--version")
    session.run(
        f"{session.bin}/python{session.python}",
        "-Im",
        "isort",
        "--check-only",
        "--diff",
        "src/",
        "tests/",
        "docs/",
        "noxfile.py",
    )


# Linters.
# -----------------------------------------------------------------------------------


@nox.session(python=["3.11"], tags=["linters", "security"])
def lint_bandit(session: nox.Session) -> None:
    """
    Lint code with the Bandit security analyzer.

    """
    session.install("bandit[toml]")
    session.run(f"{session.bin}/python{session.python}", "-Im", "bandit", "--version")
    session.run(
        f"{session.bin}/python{session.python}",
        "-Im",
        "bandit",
        "-c",
        "./pyproject.toml",
        "-r",
        "src/",
        "tests/",
    )


@nox.session(python=["3.11"], tags=["linters"])
def lint_flake8(session: nox.Session) -> None:
    """
    Lint code with flake8.

    """
    session.install("flake8", "flake8-bugbear")
    session.run(f"{session.bin}/python{session.python}", "-Im", "flake8", "--version")
    session.run(
        f"{session.bin}/python{session.python}",
        "-Im",
        "flake8",
        "src/",
        "tests/",
        "docs/",
        "noxfile.py",
    )


# Packaging checks.
# -----------------------------------------------------------------------------------


@nox.session(python=["3.11"], tags=["packaging"])
def package_build(session: nox.Session) -> None:
    """
    Check that the package builds.

    """
    session.install("build")
    session.run(f"{session.bin}/python{session.python}", "-Im", "build", "--version")
    session.run(f"{session.bin}/python{session.python}", "-Im", "build")


@nox.session(python=["3.11"], tags=["packaging"])
def package_description(session: nox.Session) -> None:
    """
    Check that the package description will render on the Python Package Index.

    """
    package_dir = session.create_tmp()
    session.install("build", "twine")
    session.run(f"{session.bin}/python{session.python}", "-Im", "build", "--version")
    session.run(f"{session.bin}/python{session.python}", "-Im", "twine", "--version")
    session.run(
        f"{session.bin}/python{session.python}",
        "-Im",
        "build",
        "--wheel",
        "--outdir",
        f"{package_dir}/build",
    )
    session.run(
        f"{session.bin}/python{session.python}",
        "-Im",
        "twine",
        "check",
        f"{package_dir}/build/*",
    )


@nox.session(python=["3.11"], tags=["packaging"])
def package_manifest(session: nox.Session) -> None:
    """
    Check that the set of files in the package matches the set under version control.

    """
    session.install("check-manifest")
    session.run(
        f"{session.bin}/python{session.python}", "-Im", "check_manifest", "--version"
    )
    session.run(
        f"{session.bin}/python{session.python}", "-Im", "check_manifest", "--verbose"
    )


@nox.session(python=["3.11"], tags=["packaging"])
def package_pyroma(session: nox.Session) -> None:
    """
    Check package quality with pyroma.

    """
    session.install("pyroma")
    session.run(
        f"{session.bin}/python{session.python}",
        "-c",
        'from importlib.metadata import version; print(version("pyroma"))',
    )
    session.run(f"{session.bin}/python{session.python}", "-Im", "pyroma", ".")


@nox.session(python=["3.11"], tags=["packaging"])
def package_wheel(session: nox.Session) -> None:
    """
    Check the built wheel package for common errors.

    """
    package_dir = session.create_tmp()
    session.install("build", "check-wheel-contents")
    session.run(f"{session.bin}/python{session.python}", "-Im", "build", "--version")
    session.run(
        f"{session.bin}/python{session.python}",
        "-Im",
        "check_wheel_contents",
        "--version",
    )
    session.run(
        f"{session.bin}/python{session.python}",
        "-Im",
        "build",
        "--wheel",
        "--outdir",
        f"{package_dir}/build",
    )
    session.run(
        f"{session.bin}/python{session.python}",
        "-Im",
        "check_wheel_contents",
        f"{package_dir}/build",
    )

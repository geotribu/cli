#! python3  # noqa: E265

"""Setup script to package into a Python module."""

# ############################################################################
# ########## Libraries #############
# ##################################

# standard library
from pathlib import Path
from typing import Union

# 3rd party
from setuptools import find_packages, setup

# package (to get version)
from geotribu_cli import __about__

# ############################################################################
# ########### Globals ##############
# ##################################

# The directory containing this file
HERE = Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text()


# ############################################################################
# ########### Functions ############
# ##################################


def load_requirements(requirements_files: Union[Path, list[Path]]) -> list:
    """Helper to load requirements list from a path or a list of paths.

    Args:
        requirements_files (Path | list[Path]): path or list to paths of requirements
            file(s)

    Returns:
        list: list of requirements loaded from file(s)
    """
    out_requirements = []

    if isinstance(requirements_files, Path):
        requirements_files = [
            requirements_files,
        ]

    for requirements_file in requirements_files:
        with requirements_file.open(encoding="UTF-8") as f:
            out_requirements += [
                line
                for line in f.read().splitlines()
                if not line.startswith(("#", "-")) and len(line)
            ]

    return out_requirements


# ############################################################################
# ########### Main #################
# ##################################

setup(
    name=__about__.__package_name__,
    author=__about__.__author__,
    author_email=__about__.__email__,
    description=__about__.__summary__,
    long_description=README,
    long_description_content_type="text/markdown",
    keywords=__about__.__keywords__,
    url=__about__.__uri_homepage__,
    project_urls={
        "Docs": __about__.__uri_homepage__,
        "Bug Reports": __about__.__uri_tracker__,
        "Source": __about__.__uri_repository__,
    },
    version=__about__.__version__,
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Intended Audience :: Information Technology",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
        "Topic :: Scientific/Engineering :: GIS",
    ],
    # packaging
    py_modules=["geotribu_cli"],
    packages=find_packages(
        exclude=["contrib", "docs", "*.tests", "*.tests.*", "tests.*", "tests", ".venv"]
    ),
    include_package_data=True,
    install_requires=load_requirements(HERE / "requirements/base.txt"),
    extras_require={
        # tooling
        "dev": load_requirements(HERE / "requirements/development.txt"),
        "doc": load_requirements(HERE / "requirements/documentation.txt"),
        "test": load_requirements(HERE / "requirements/testing.txt"),
        # functional
        "all": load_requirements(
            list(HERE.joinpath("requirements").glob("extra.*.txt"))
        ),
        "img-local": load_requirements(HERE / "requirements/extra.img-local.txt"),
        "img-remote": load_requirements(HERE / "requirements/extra.img-remote.txt"),
    },
    # cli
    entry_points={
        "console_scripts": [
            f"{__about__.__executable_name__} = geotribu_cli.cli:main",
            "geotribu-cli = geotribu_cli.cli:main",
        ]
    },
)

#!/usr/bin/env python3

VERSION = "0.0.10"

DESCRIPTION = "Python module for composing computations"
CLASSIFIERS = [
    "Intended Audience :: Developers",
    "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
    "Natural Language :: English",
    "Operating System :: OS Independent",
    "Programming Language :: Python :: 3",
    "Topic :: Software Development :: Libraries :: Python Modules",
]


def main():
    try:
        from setuptools import setup
    except ImportError:
        from distutils.core import setup

    with open("README.md") as fin:
        desc = fin.read().strip()

    options = {
        "name": "fppy",
        "version": VERSION,
        "license": "GPLv3",
        "description": DESCRIPTION,
        "long_description": desc,
        "long_description_content_type": "text/markdown",
        "url": "https://github.com/Z-Shang/fpy",
        "author": "zshang",
        "author_email": "z@gilgamesh.me",
        "classifiers": CLASSIFIERS,
        "packages": [
            "fpy",
            "fpy.composable",
            "fpy.control",
            "fpy.data",
            "fpy.debug",
            "fpy.experimental",
            "fpy.parsec",
            "fpy.utils",
            "fpy.tests",
        ],
        "install_requires": ["bytecode"],
    }
    setup(**options)


if __name__ == "__main__":
    main()

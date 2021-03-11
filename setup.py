#!/usr/bin/env python3

VERSION = "0.0.1"

DESCRIPTION = "Python module for composing computations"
CLASSIFIERS = [
    "Intended Audience :: Developers",
    "License :: OSI Approved :: GPLv3",
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

    with open("README.mkd") as fin:
        desc = fin.read().strip()

    options = {
        "name": "fpy",
        "version": VERSION,
        "license": "GPLv3",
        "description": DESCRIPTION,
        "long_description": desc,
        "url": "https://github.com/Z-Shang/fpy",
        "author": "Z.Shang",
        "author_email": "z@gilgamesh.me",
        "classifiers": CLASSIFIERS,
        "packages": ["fpy", "fpy.tests"],
    }
    setup(**options)


if __name__ == "__main__":
    main()

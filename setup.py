#!/usr/bin/env python

from setuptools import setup
from glob import glob

NAME = "botfly"

with open('README.md') as fo:
    LONG_DESCRIPTION = fo.read()


setup(
    name=NAME,
    packages=["botfly"],
    install_requires=[
        "prompt_toolkit",
    ],
    scripts=glob("bin/*"),
    setup_requires=["setuptools_scm"],
    use_scm_version=True,
    test_suite="tests",
    tests_require=["pytest"],

    description="Alternative Python debugger using prompt-toolkit.",
    long_description_content_type="text/markdown",
    long_description=LONG_DESCRIPTION,
    license="Apache 2.0",
    author="Keith Dart",
    author_email="keith@dartworks.biz",
    url="https://github.com/kdart/botfly",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 3 :: Only",
        "Topic :: Software Development :: Debuggers",
    ],
)

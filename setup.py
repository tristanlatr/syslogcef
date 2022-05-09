#! /usr/bin/env python3
from setuptools import setup, find_packages
import pathlib
# The directory containing this file
HERE = pathlib.Path(__file__).parent
# About the project
ABOUT = {}
exec((HERE / "syslogcef" / "__version__.py").read_text(), ABOUT)
# The text of the README file
README = (HERE / "README.md").read_text()
setup(
    name                =   ABOUT['__title__'],
    description         =   ABOUT['__description__'],
    url                 =   ABOUT['__url__'],
    version             =   ABOUT['__version__'],
    packages            =   find_packages(exclude=('tests')), 
    classifiers         =   ["Programming Language :: Python :: 3",],
    license             =   ABOUT['__license__'],
    long_description    =   README,
    long_description_content_type   =   "text/markdown",
    python_requires     =   '>=3.6',
    install_requires    =   ['rfc5424-logging-handler', 
                             'cefevent>=0.5.3',],
    extras_require      =   {'dev': ["tox"]},
    keywords            =   ABOUT['__keywords__'],
)

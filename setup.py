#/usr/bin/env python
import os
from setuptools import setup, find_packages

ROOT_DIR = os.path.dirname(__file__)
SOURCE_DIR = os.path.join(ROOT_DIR)

setup(
    name="django_haikus",
    description="Some classes for finding haikus in text",
    author="Grant Thomas",
    author_email="grant.thomas@wk.com",
    url="https://github.com/wieden-kennedy/django_haikus",
    version="0.0.1",
    dependency_links = ['http://github.com/wieden-kennedy/haikus/tarball/master#egg=haikus'],
    install_requires=["haikus","nltk","django>=1.2.1","redis","elementtree"],
    packages=['django_haikus'],
    package_data={'django_haikus':['templates/*','static/*']},
    zip_safe=False,
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Development Status :: 4 - Beta",
        "Environment :: Web Environment",
        "Framework :: Django",
        "Intended Audience :: Developers",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
)

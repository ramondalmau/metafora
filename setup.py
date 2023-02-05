#!/usr/bin/env python
from setuptools import setup, find_packages

setup(name='metafora',
      version='1.0',
      description='METAR and TAF parser with dataclasses and regular expressions',
      author='Ramon Dalmau-Codina',
      author_email='ramon.dalmau-codina@eurocontrol.int',
      url='https://github.com/ramondalmau/metafora.git',
      packages=find_packages(),
      python_requires='>=3.7',
      install_requires=[
          'dataclasses>=0.6',
          'marshmallow>=3.17.0',
          'dataclasses-json>=0.5.7']
      )

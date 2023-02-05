#!/usr/bin/env python
from setuptools import setup

setup(name='metafora',
      version='0.1.3',
      description='METAR and TAF parser with dataclasses and regular expressions',
      author='Ramon Dalmau-Codina',
      author_email='ramon.dalmau.codina@gmail.com',
      url='https://github.com/ramondalmau/metafora.git',
      packages=["metafora"],
      python_requires='>=3.7',
      install_requires=[
          'dataclasses>=0.6',
          'marshmallow>=3.17.0',
          'dataclasses-json>=0.5.7']
      )

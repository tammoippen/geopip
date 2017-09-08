# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals

from setuptools import find_packages, setup

try:
    import pypandoc
    long_description = pypandoc.convert('README.md', 'rst')
except(IOError, ImportError):
    long_description = open('README.md').read()


version = '0.4'

setup(
    name='geopip',
    version=version,
    packages=find_packages(),
    install_requires=[
        'geohash2',
        # 'numpy',
        # 'shapely[vectorized]>=1.6b4',
    ],
    author='Tammo Ippen',
    author_email='tammo.ippen@posteo.de',
    description='Reverse geocode a lng/lat coordinate within a geojson FeatureCollection.',
    long_description=long_description,
    url='https://github.com/tammoippen/geopip',
    download_url='https://github.com/tammoippen/geopip/archive/v{}.tar.gz'.format(version),
    keywords=['geojson', 'point in polygon', 'reverse geocode', 'countries'],
    include_package_data=True,
)

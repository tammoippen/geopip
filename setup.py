# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals

from setuptools import find_packages, setup


setup(
    name='geopip',
    version='0.2',
    packages=find_packages(),
    install_requires=[
        'geohash2',
        # 'numpy',
        # 'shapely[vectorized]>=1.6b4',
    ],
    author='Tammo Ippen',
    author_email='tammo.ippen@posteo.de',
    description='Reverse geocode a lng/lat coordinate within a geojson FeatureCollection.',
    url='https://github.com/tammoippen/geopip',
    download_url='https://github.com/tammoippen/geopip/archive/v0.2.tar.gz',
    keywords=['geojson', 'point in polygon', 'reverse geocode', 'countries'],
    include_package_data=True,
)

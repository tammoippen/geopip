# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals

# The MIT License
#
# Copyright (c) 2017 Tammo Ippen, tammo.ippen@posteo.de
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

from geohash2 import encode

from ._geo_fkt import bbox_hash, in_bbox
from ._geojson import geojson

try:
    from ._shapely import prepare, p_in_polygon
except ImportError:
    from ._pure import prepare, p_in_polygon


_SHAPES = None
def shapes():  # noqa: E302
    '''Return preprocessed shapes for `search` lookup.

    Preprocess geojson features depending on the search backend. Group shapes by
    the geohash of its bounding box, i.e. the first geohash rectangle that fully
    contains the bbox. This results (more-or-less) in a quad-tree and gives fast
    lookups (best case O(log(n)); worst case still O(n) ).

    Returns:
        Dict[str, List[Dict[str, Any]]]: Preprocessed shapes.
    '''
    global _SHAPES
    if _SHAPES is not None:
        return _SHAPES

    data = geojson()

    _SHAPES = dict()  # geohash -> shapes
    for feat in data['features']:
        for shp in prepare(feat):
            key = bbox_hash(shp['bounds'])
            shp['geohash'] = key
            if key not in _SHAPES:
                _SHAPES[key] = []
            _SHAPES[key].append(shp)

    return _SHAPES


def search_all(lng, lat):
    '''Reverse geocode lng/lat coordinate within the features from `shapes`.

    Look within the features from the `shapes()` function for all polygon that
    contains the point (lng, lat). From all found feature the `porperties`
    will be returned (more or less sorted from smallest to largest feature).
    `None`, if no feature containes the point.

    Parameters:
        lng: float  Longitude (-180, 180) of point. (WGS84)
        lat: float  Latitude (-90, 90) of point. (WGS84)

    Returns:
        Iterator[Dict[Any, Any]]  Iterator for `properties` of found features.
    '''
    if not (-180 <= lng <= 180):
        raise ValueError('Longitude must be between -180 and 180.')
    if not (-90 <= lat <= 90):
        raise ValueError('Latitude must be between -90 and 90.')

    key = encode(latitude=lat, longitude=lng)
    for sub_key in [key] + [key[:-i] for i in range(1, len(key))]:
        # look withing geohash rectangles of increasing resolution
        for shp in shapes().get(sub_key, []):
            # look through all shapes within one resolution
            if in_bbox((lng, lat), shp['bounds']):
                # first check if point in bbox
                if p_in_polygon((lng, lat), shp):
                    # ensure point is in polygon
                    yield shp['properties']
                    # look for other overlaps


def search(lng, lat):
    '''Reverse geocode lng/lat coordinate within the features from `shapes`.

    Look within the features from the `shapes()` function for a polygon that
    contains the point (lng, lat). From the first found feature the `porperties`
    will be returned. `None`, if no feature containes the point.

    Parameters:
        lng: float  Longitude (-180, 180) of point. (WGS84)
        lat: float  Latitude (-90, 90) of point. (WGS84)

    Returns:
        Dict[Any, Any]  `Properties` of found feature. `None` if nothing is found.
    '''
    try:
        return next(search_all(lng, lat))
    except StopIteration:
        return None

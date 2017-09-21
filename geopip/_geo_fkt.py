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

from os.path import commonprefix

from geohash_hilbert import encode


def bbox(shp):
    '''Compute the bounding box of the given shape (Polygon and MultiPolygon allowed).

    If `shp` already contains a `bbox` member, return that instead.

    Parameters:
        shp: Dict[str, Any]  geojson feature, that is either a Polygon or MultiPolygon

    Returns:
        Tuple[float, float, float, float]: Bounding box of `shp`: minlng, minlat, maxlng, maxlat
    '''
    if shp.get('bbox'):
        return shp['bbox']

    if shp['type'] == 'Polygon':
        coords = (p for p in shp['coordinates'][0])
    elif shp['type'] == 'MultiPolygon':
        coords = (p for poly in shp['coordinates'] for p in poly[0])
    else:
        raise ValueError('Expect Polygon or MultiPolygon.')

    minlng, maxlng, minlat, maxlat = None, None, None, None

    for lng, lat in coords:
        if minlng is None:
            minlng, maxlng = lng, lng
            minlat, maxlat = lat, lat
        minlat = min(lat, minlat)
        minlng = min(lng, minlng)
        maxlat = max(lat, maxlat)
        maxlng = max(lng, maxlng)

    return minlng, minlat, maxlng, maxlat


def in_bbox(p, bbox):
    '''Test, whether point p (lng,lat) is in bbox (minlng, minlat, maxlng, maxlat)

    Parameters:
        p: Tuple[float, float]  2D point (lng, lat) (WGS84) Longitude (-180, 180) Latitude (-90, 90)
        bbox: Tuple[float, float, float, float]  Bounding box, (minlng, minlat, maxlng, maxlat)

    Returns:
        bool: True, if point is in bbox, False otherwise.
    '''
    lng, lat = p
    minlng, minlat, maxlng, maxlat = bbox
    return minlng <= lng <= maxlng and minlat <= lat <= maxlat


def bbox_hash(bbox):
    '''Get geohash from rectangle covering the complete bbox.

    Parameters:
        bbox: Tuple[float, float, float, float]  Bounding box, (minlng, minlat, maxlng, maxlat)

    Returns:
        str: geohash covering the complete bbox.
    '''
    minlng, minlat, maxlng, maxlat = bbox

    # ensure values are in range
    minlng = max(-180, minlng)
    maxlng = min(180, maxlng)
    minlat = max(-90, minlat)
    maxlat = min(90, maxlat)

    ll = encode(lng=minlng, lat=minlat, precision=16, bits_per_char=4)
    ur = encode(lng=maxlng, lat=maxlat, precision=16, bits_per_char=4)

    return commonprefix((ll, ur))


def ccw(a, b, c):
    '''Tests whether the turn formed by a, b, and c is CCW

    Returns:
        > 0 for c left of the line through a and b (ccw)
        = 0 for b on the line
        < 0 for b right of the line (not ccw)
    '''
    return (b[0] - a[0]) * (c[1] - a[1]) - (c[0] - a[0]) * (b[1] - a[1])


# def is_convex(ring):  # TODO not used: maybe use for faster p_in_p test
#     n = len(ring)
#     for i in range(2, n):
#         p0 = ring[(i - 2) % n]
#         p1 = ring[(i - 1) % n]
#         p2 = ring[i % n]
#         if ccw(p0, p1, p2) > 0:
#             return False
#     return True


def winding_number(p, ring):
    '''Return the winding number of `p` wrt `ring`.

    If the winding number is 0, then p is outside of the ring.

    Parameters:
        p: Tuple[float, float]           2D Point.
        ring: List[Tuple[float, float]]  Ring of Points in CCW orientation (ring[0] == ring[-1]).

    Returns:
        int: the winding number (=0 only if `p` is outside `ring`)
    '''
    n = len(ring)
    wn = 0
    for i in range(1, n):
        p1 = ring[i - 1]
        p2 = ring[i]

        if p1[1] <= p[1]:
            if p2[1] > p[1]:
                if ccw(p1, p2, p) > 0:
                    wn += 1
        else:
            if p2[1] <= p[1]:
                if ccw(p1, p2, p) < 0:
                    wn -= 1
    return wn


def p_in_polygon(p, polygon):
    '''Test, whether `p` is in the polygon.

    Parameters:
        p: Tuple[float, float]                    2D Point.
        polygon: List[List[Tuple[float, float]]]  Polygon, i.e. one exterior ring,
                                                  and multiple interior rings (holes).

    Returns:
        bool: True, if `p` in `polygon`, False otherwise.
    '''
    assert len(polygon) >= 1

    if winding_number(p, polygon[0]) != 0:
        # p inside polygon
        # check p not inside one of the holes
        for hole in polygon[1:]:
            if winding_number(p, hole) != 0:
                return False  # in hole of polygon
        return True

    return False

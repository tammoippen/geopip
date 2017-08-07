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

from shapely import speedups
from shapely.geometry import Point, shape
from shapely.prepared import prep

speedups.enable()


def prepare(feat):
    '''Prepare geojson feature for further processing in `geopip._shapely.p_in_polygon()`

    Parameters:
        feat: Dict[str, Any]  Geojson feature (only Polygon and MultiPolygon will
                              be processed).

    Returns:
        List[Dict[str, Any]]  Prepared shapes for `geopip._shapely.p_in_polygon()`
    '''
    if feat['geometry']['type'] in ('Polygon', 'MultiPolygon'):
        shp = shape(feat['geometry'])
        return [dict(
            shape=prep(shp),
            properties=feat['properties'],
            bounds=shp.bounds
        )]
    else:
        return []


def p_in_polygon(p, shp):
    '''Test, whether point `p` is in shape `shp`.

    Use the shapely implementation.

    Parameters:
        p: Tuple[float, float]  Point (lng, lat) in WGS84.
        shp: Dict[str, Any]     Prepared shape dictionary from `geopip._shapely.prepare()`.

    Returns:
        boolean: True, if p in shp, False otherwise
    '''
    return shp['shape'].contains(Point(*p))

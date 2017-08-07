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

from ._geo_fkt import bbox
from ._geo_fkt import p_in_polygon as pure_p_in_polygon


def prepare(feat):
    '''Prepare geojson feature for further processing in `geopip._pure.p_in_polygon()`

    Parameters:
        feat: Dict[str, Any]  Geojson feature (only Polygon and MultiPolygon will
                              be processed).

    Returns:
        List[Dict[str, Any]]  Prepared shapes for `geopip._pure.p_in_polygon()`
    '''
    shp = feat['geometry']
    res = []
    if shp['type'] == 'MultiPolygon':
        for p_coords in shp['coordinates']:
            polygon = dict(
                type='Polygon',
                coordinates=p_coords
            )
            res += [dict(
                shape=polygon,
                properties=feat['properties'],
                bounds=bbox(polygon)
            )]
    elif shp['type'] == 'Polygon':
        res += [dict(
            shape=shp,
            properties=feat['properties'],
            bounds=bbox(shp)
        )]
    return res


def p_in_polygon(p, shp):
    '''Test, whether point `p` is in shape `shp`.

    Use the pure python implementation.

    Parameters:
        p:   Tuple[float, float]  Point (lng, lat) in WGS84.
        shp: Dict[str, Any]       Prepared shape dictionary from `geopip._pure.prepare()`.

    Returns:
        boolean: True, if p in shp, False otherwise
    '''
    return pure_p_in_polygon(p, shp['shape']['coordinates'])

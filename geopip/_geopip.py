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
import importlib.resources
import json
import sys
from os import environ

from geohash_hilbert import encode

from ._geo_fkt import bbox_hash, in_bbox

try:
    from ._shapely import p_in_polygon, prepare

    SHAPELY_AVAILABLE = True
except ImportError:
    from ._pure import p_in_polygon, prepare

    SHAPELY_AVAILABLE = False

_MIN_LNG = -180
_MAX_LNG = 180
_MIN_LAT = -90
_MAX_LAT = 90


class GeoPIP(object):
    """GeoPIP: Geojson Point in Polygon (PIP)

    Reverse geocode a lng/lat coordinate within a geojson `FeatureCollection` and
    return information about the containing polygon.
    """

    def __init__(self, filename=None, geojson_dict=None):
        """Provide the geojson either as a file (`filename`) or as a geojson
        dict (`geojson_dict`). If none of both is given, it tries to load the
        file pointed to in the environment variable `REVERSE_GEOCODE_DATA`. If the
        variable is not set, a default geojson will be loaded (packaged):
            http://thematicmapping.org/downloads/world_borders.php

        During init, the geojson will be prepared (see pure / shapely implementation)
        and indexed with geohashes.

        Parameters:
            filename: str                 Path to a geojson file.
            geojson_dict: Dict[str, Any]  Geojson dictionary. `FeatureCollection` required!
        """
        if filename and geojson_dict:
            raise ValueError("Only one of `filename` or `geojson_dict` is allowed!")

        self._source = None
        data = None
        if filename is not None:
            with open(filename, "r", encoding="utf-8") as f:
                data = json.load(f)
            self._source = filename
        elif geojson_dict is not None:
            data = geojson_dict
            self._source = "<dict>"
        elif environ.get("REVERSE_GEOCODE_DATA"):
            # load default
            with open(environ["REVERSE_GEOCODE_DATA"], "r", encoding="utf-8") as f:
                data = json.load(f)
            self._source = "<env = " + environ["REVERSE_GEOCODE_DATA"] + " >"
        else:
            if sys.version_info >= (3, 9):
                data = json.loads(
                    importlib.resources.files("geopip")
                    .joinpath("globe.geo.json")
                    .read_bytes()
                )
            else:
                data = json.loads(
                    importlib.resources.read_binary("geopip", "globe.geo.json")
                )
            self._source = "<package-data>"

        if not isinstance(data, dict) or data.get("type") != "FeatureCollection":
            raise ValueError("Only `FeatureCollections` are allowed as input!")

        # initialize during init!
        self._shapes = GeoPIP._initialize_shapes(data)

    @staticmethod
    def _initialize_shapes(data):
        shapes = {}  # geohash -> shapes
        for feat in data["features"]:
            for shp in prepare(feat):
                key = bbox_hash(shp["bounds"])
                shp["geohash"] = key
                if key not in shapes:
                    shapes[key] = []
                shapes[key].append(shp)

        return shapes

    def __str__(self):
        return "GeoPIP from {}: {} hashes, {} polygons".format(
            self._source, len(self.shapes), sum(len(ps) for ps in self.shapes.values())
        )

    @property
    def shapes(self):
        return self._shapes

    def search_all(self, lng, lat):
        """Reverse geocode lng/lat coordinate within the features from `self.shapes`.

        Look within the features from `self.shapes` for all polygon that
        contains the point (lng, lat). From all found feature the `porperties`
        will be returned (more or less sorted from smallest to largest feature).
        `None`, if no feature containes the point.

        Parameters:
            lng: float  Longitude (-180, 180) of point. (WGS84)
            lat: float  Latitude (-90, 90) of point. (WGS84)

        Returns:
            Iterator[Dict[Any, Any]]  Iterator for `properties` of found features.
        """
        if not (_MIN_LNG <= lng <= _MAX_LNG):
            raise ValueError("Longitude must be between -180 and 180.")
        if not (_MIN_LAT <= lat <= _MAX_LAT):
            raise ValueError("Latitude must be between -90 and 90.")

        key = encode(lng=lng, lat=lat, precision=16, bits_per_char=4)
        for sub_key in [key] + [key[:-i] for i in range(1, len(key) + 1)]:
            # look withing geohash rectangles of increasing resolution
            for shp in self.shapes.get(sub_key, []):
                # look through all shapes within one resolution
                if in_bbox((lng, lat), shp["bounds"]):
                    # first check if point in bbox
                    if p_in_polygon((lng, lat), shp):
                        # ensure point is in polygon
                        yield shp["properties"]
                        # look for other overlaps

    def search(self, lng, lat):
        """Reverse geocode lng/lat coordinate within the features from `self.shapes`.

        Look within the features from `self.shapes` for a polygon that
        contains the point (lng, lat). From the first found feature the `porperties`
        will be returned. `None`, if no feature containes the point.

        Parameters:
            lng: float  Longitude (-180, 180) of point. (WGS84)
            lat: float  Latitude (-90, 90) of point. (WGS84)

        Returns:
            Dict[Any, Any]  `Properties` of found feature. `None` if nothing is found.
        """
        try:
            return next(self.search_all(lng, lat))
        except StopIteration:
            return None

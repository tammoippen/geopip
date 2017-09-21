# GEOPIP: Geojson Point in Polygon (PIP)

[![Build Status](https://travis-ci.org/tammoippen/geopip.svg?branch=master)](https://travis-ci.org/tammoippen/geopip)
[![Coverage Status](https://coveralls.io/repos/github/tammoippen/geopip/badge.svg?branch=master)](https://coveralls.io/github/tammoippen/geopip?branch=master)
[![Tested CPython Versions](https://img.shields.io/badge/cpython-2.7%2C%203.5%2C%203.6%2C%20nightly-brightgreen.svg)](https://img.shields.io/badge/cpython-2.7%2C%203.5%2C%203.6%2C%20nightly-brightgreen.svg)
[![Tested PyPy Versions](https://img.shields.io/badge/pypy-2.7--5.8.0%2C%203.5--5.8.0-brightgreen.svg)](https://img.shields.io/badge/pypy-2.7--5.8.0%2C%203.5--5.8.0-brightgreen.svg)
[![PyPi version](https://img.shields.io/pypi/v/geopip.svg)](https://pypi.python.org/pypi/geopip)
[![PyPi license](https://img.shields.io/pypi/l/geopip.svg)](https://pypi.python.org/pypi/geopip)

Reverse geocode a lng/lat coordinate within a geojson `FeatureCollection` and return information about the containing country (polygon).

Basically, you can use any [geojson](https://tools.ietf.org/html/rfc7946) file (top level is a `FeatureCollection`) for reverse coding - set the environment variable `REVERSE_GEOCODE_DATA` to the geojson file. Only `Polygon` and `MultiPolygon` features will be used! If a point is found to be in a feature, the `properties` of that feature will be returned.

The default shape data (contained within the package) is from [thematicmapping](http://thematicmapping.org/downloads/world_borders.php) (the simple shapes). It contains polygons representing one country with the following meta-data (`properties`):
```
FIPS      String(2)         FIPS 10-4 Country Code
ISO2      String(2)         ISO 3166-1 Alpha-2 Country Code
ISO3      String(3)         ISO 3166-1 Alpha-3 Country Code
UN        Short Integer(3)  ISO 3166-1 Numeric-3 Country Code
NAME      String(50)        Name of country/area
AREA      Long Integer(7)   Land area, FAO Statistics (2002)
POP2005   Double(10,0)      Population, World Population Prospects (2005)
REGION    Short Integer(3)  Macro geographical (continental region), UN Statistics
SUBREGION Short Integer(3)  Geographical sub-region, UN Statistics
LON       FLOAT (7,3)       Longitude
LAT       FLOAT (6,3)       Latitude
```

Hence, you can use this package as an *offline reverse geocoder on the country level* (by default):
```python
In [1]: import geopip
In [2]: geopip.search(lng=4.910248, lat=50.850981)
Out[2]:
{'AREA': 0,
 'FIPS': 'BE',
 'ISO2': 'BE',
 'ISO3': 'BEL',
 'LAT': 50.643,
 'LON': 4.664,
 'NAME': 'Belgium',
 'POP2005': 10398049,
 'REGION': 150,
 'SUBREGION': 155,
 'UN': 56}
```

**NOTE**: Since the polygons for each country are quite simple, reverse geocoding at the borders of two countrys is **not** exact. Use polygons with higher resolution for these use cases (see [Data](#data)).

The `shapely` package will be used, if installed. Otherwise, a pure python implementation will be used (on the basis of [winding numbers](https://en.wikipedia.org/wiki/Winding_number)). See [here](https://www.toptal.com/python/computational-geometry-in-python-from-theory-to-implementation), [here](http://geomalgorithms.com/a03-_inclusion.html) and [here](http://www.dgp.toronto.edu/~mac/e-stuff/point_in_polygon.py) for more informations and example implementations. Espacially for larger features, the shapely implementation might give performance improvements (default shape data and 2.6 GHz Intel Core i7, python3.6.2):

*Pure*:
```python
In [1]: import geopip
In [2]: geopip._geopip.p_in_polygon?
Signature: geopip._geopip.p_in_polygon(p, shp)
Docstring:
Test, whether point `p` is in shape `shp`.

Use the pure python implementation for this.

Parameters:
    p: Tuple[float, float]  Point (lng, lat) in WGS84.
    shp: Dict[str, Any]     Prepared shape dictionary from `geopip._pure.prepare()`.

Returns:
    boolean: True, if p in shp, False otherwise
File:      ~/repositories/geopip/geopip/_pure.py
Type:      function
In [3]: %timeit geopip.search(4.910248, 50.850981)
64.4 µs ± 1.7 µs per loop (mean ± std. dev. of 7 runs, 10000 loops each)
```

*Shapely*:
```python
In [1]: import geopip
In [2]: geopip_geopip.p_in_polygon?
Signature: geopip._geopip.p_in_polygon(p, shp)
Docstring:
Test, whether point `p` is in shape `shp`.

Use the shapely implementation for this.

Parameters:
    p: Tuple[float, float]  Point (lng, lat) in WGS84.
    shp: Dict[str, Any]     Prepared shape dictionary from `geopip._shapely.prepare()`.

Returns:
    boolean: True, if p in shp, False otherwise
File:      ~/repositories/geopip/geopip/_shapely.py
Type:      function
In [3]: %timeit geopip.search(4.910248, 50.850981)
87.1 µs ± 1.52 µs per loop (mean ± std. dev. of 7 runs, 10000 loops each)
```

# Data

Other interesting shape data can be found at:

- http://www.naturalearthdata.com/downloads/ : Different thematic shape files at 10m, 50m and 110m resolution.
- http://www.gadm.org/version2 : Administrative area 0 or 1 contain contries or states, respectively. Attention to the license!
- https://www2.census.gov/geo/tiger/: Various shape/gdb files and information for USA.
- http://guides.library.upenn.edu/c.php?g=475518&p=3254770: Links to various geoinformation data.
- http://thematicmapping.org/downloads/world_borders.php: Country borders and some interesting information. The default file is from here. There is also a higher resolution version.
- https://github.com/evansiroky/timezone-boundary-builder: Time zone boundaries. See releases for downloads.

**NOTE**: shapefiles / gdb databases have to be transformed into geojson. One way is to use [fiona](https://github.com/Toblerity/Fiona). Assuming the gdb files are in the directory `/data/gdb`:

```python
fio insp /data/gdb
# a python shell opens
>>> import json
>>> features = []
>>> for feat in src:
...     features += [feat]
...
>>> f = open('/data/gdb.geo.json', 'w')
>>> json.dump(dict(type='FeatureCollection', features=features), f)
>>> f.close()
```
Then the `gdb` will be transformed into a geojson file `gdb.geo.json`.

# Documentation

(*TODO* more)
Basically, there are the two functions `geopip.search` and `geopip.search_all` that perform the search in the provided `FeatureCollection`. Then there is the class `geopip.GeoPIP` that accepts a `FeatureCollection` either as a file or a dictionary and provides the same search functionality:

## `search`
```python
In [1]: import geopip
In [2]: geopip.search?
Signature: geopip.search(lng, lat)
Docstring:
Reverse geocode lng/lat coordinate within the features from `instance().shapes`.

Look within the features from the `instance().shapes` function for a polygon that
contains the point (lng, lat). From the first found feature the `porperties`
will be returned. `None`, if no feature containes the point.

Parameters:
    lng: float  Longitude (-180, 180) of point. (WGS84)
    lat: float  Latitude (-90, 90) of point. (WGS84)

Returns:
    Dict[Any, Any]  `Properties` of found feature. `None` if nothing is found.
File:      ~/repositories/geopip/geopip/__init__.py
Type:      function
```

## `search_all`
```python
In [1]: import geopip
In [2]: geopip.search_all?
Signature: geopip.search_all(lng, lat)
Docstring:
Reverse geocode lng/lat coordinate within the features from `instance().shapes`.

Look within the features from the `instance().shapes` function for all polygon that
contains the point (lng, lat). From all found feature the `porperties`
will be returned (more or less sorted from smallest to largest feature).
`None`, if no feature containes the point.

Parameters:
    lng: float  Longitude (-180, 180) of point. (WGS84)
    lat: float  Latitude (-90, 90) of point. (WGS84)

Returns:
    Iterator[Dict[Any, Any]]  Iterator for `properties` of found features.
File:      ~/repositories/geopip/geopip/__init__.py
Type:      function
```

## `GeoPIP`
```python
In [1]: import geopip
In [2]: geopip.GeoPIP?
Init signature: geopip.GeoPIP(self, *args, **kwargs)
Docstring:
GeoPIP: Geojson Point in Polygon (PIP)

Reverse geocode a lng/lat coordinate within a geojson `FeatureCollection` and
return information about the containing polygon.
Init docstring:
Provide the geojson either as a file (`filename`) or as a geojson
dict (`geojson_dict`). If none of both is given, it tries to load the
file pointed to in the environment variable `REVERSE_GEOCODE_DATA`. If the
variable is not set, a default geojson will be loaded (packaged):
    http://thematicmapping.org/downloads/world_borders.php

During init, the geojson will be prepared (see pure / shapely implementation)
and indexed with geohashes.

Provide the parameters as kwargs!

Allowed parameters:
    filename: str                 Path to a geojson file.
    geojson_dict: Dict[str, Any]  Geojson dictionary. `FeatureCollection` required!
File:           ~/repositories/geopip/geopip/_geopip.py
Type:           type
```

A `GeoPIP` object provides the same `search` and `search_all` functions.

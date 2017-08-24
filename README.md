# GEOPIP: Geojson Point in Polygon (PIP)

[![Build Status](https://travis-ci.org/tammoippen/geopip.svg?branch=master)](https://travis-ci.org/tammoippen/geopip)

Reverse geocode a lng/lat coordinate within a geojson `FeatureCollection` and return information about the containing country (polygon).

Basically, you can use any [geojson](https://tools.ietf.org/html/rfc7946) file (top level is a `FeatureCollection`) for reverse coding - set the environment variable `REVERSE_GEOCODE_DATA` to the geojson file. Only `Polygon` and `MultiPolygon` features will be used! If a point is found to be in a feature, the `properties` of that feature will be returned.

The default shape data (contained within the package) is from [tematicmapping](http://thematicmapping.org/downloads/world_borders.php) (the simple shapes). It contains polygons representing one country with the following meta-data (`properties`):
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
In [2]: geopip.p_in_polygon?
Signature: geopip.p_in_polygon(p, shp)
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
In [2]: geopip.p_in_polygon?
Signature: geopip.p_in_polygon(p, shp)
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

**NOTE**: shapefiles / gdb databases have to be transformed into geojson. One way is to use [fiona](https://github.com/Toblerity/Fiona). Assuming the gdb files are in the directory `/data/gdb`:

```sh
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

# Improvements:

- Unittesting!

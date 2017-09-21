# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals

import json
from os import environ

from geopip import search, search_all
from geopip._geopip import GeoPIP
import pytest

try:
    import shapely  # noqa: F401
    SHAPELY_AVAILABLE = True
except ImportError:
    SHAPELY_AVAILABLE = False


@pytest.fixture()
def collection(testdir):
    with open(testdir + '/sample.geo.json', 'r') as f:
        return json.load(f)


def test_default_init():
    geo = GeoPIP()

    if SHAPELY_AVAILABLE:
        assert len(geo.shapes) == 97  # hashes
        assert sum(len(ps) for ps in geo.shapes.values()) == 246  # multipolygons / countries
    else:
        assert len(geo.shapes) == 2364  # hashes
        assert sum(len(ps) for ps in geo.shapes.values()) == 3697  # polygons / parts of countries

    assert isinstance(geo.shapes, dict)  # geohash -> [shapes]
    for shps in geo.shapes.values():
        for shp in shps:
            assert {'FIPS', 'ISO2', 'ISO3', 'UN', 'NAME',
                    'AREA', 'POP2005', 'REGION', 'SUBREGION',
                    'LON', 'LAT'} == set(shp['properties'].keys())

    _test_geo_locations(geo.search, geo.search_all)


def test_geopip_funktions():
    _test_geo_locations(search, search_all)


def _test_geo_locations(search_fkt, search_all_fkt):
    # search
    assert 'DE' == search_fkt(lng=7, lat=51)['ISO2']
    assert 'BE' == search_fkt(5.064697265625, 50.61113171332364)['ISO2']
    assert 'NL' == search_fkt(5.6689453125, 52.251346020673644)['ISO2']
    assert 'FR' == search_fkt(2.373046875, 48.821332549646634)['ISO2']

    assert 'GB' == search_fkt(-3.8671874999999996, 50.792047064406866)['ISO2']
    assert 'IE' == search_fkt(-8.5693359375, 53.212612189941574)['ISO2']
    assert 'PT' == search_fkt(-7.8662109375, 40.78054143186033)['ISO2']
    assert 'US' == search_fkt(-105.1171875, 40.17887331434696)['ISO2']

    assert 'NA' == search_fkt(18.28125, -19.601194161263145)['ISO2']
    assert 'MG' == search_fkt(46.7578125, -17.476432197195518)['ISO2']
    assert 'AU' == search_fkt(123.92578125, -25.48295117535531)['ISO2']

    assert 'BR' == search_fkt(-52.734375, -8.233237111274553)['ISO2']
    assert 'PE' == search_fkt(-72.24609375, -13.2399454992863)['ISO2']
    assert 'AR' == search_fkt(-66.97265625, -39.368279149160124)['ISO2']

    # search all
    assert ['DE'] == [res['ISO2'] for res in search_all_fkt(lng=7, lat=51)]
    assert ['BE'] == [res['ISO2'] for res in search_all_fkt(5.064697265625, 50.61113171332364)]
    assert ['NL'] == [res['ISO2'] for res in search_all_fkt(5.6689453125, 52.251346020673644)]
    assert ['FR'] == [res['ISO2'] for res in search_all_fkt(2.373046875, 48.821332549646634)]

    assert ['GB'] == [res['ISO2'] for res in search_all_fkt(-3.8671874999999996, 50.792047064406866)]
    assert ['IE'] == [res['ISO2'] for res in search_all_fkt(-8.5693359375, 53.212612189941574)]
    assert ['PT'] == [res['ISO2'] for res in search_all_fkt(-7.8662109375, 40.78054143186033)]
    assert ['US'] == [res['ISO2'] for res in search_all_fkt(-105.1171875, 40.17887331434696)]

    assert ['NA'] == [res['ISO2'] for res in search_all_fkt(18.28125, -19.601194161263145)]
    assert ['MG'] == [res['ISO2'] for res in search_all_fkt(46.7578125, -17.476432197195518)]
    assert ['AU'] == [res['ISO2'] for res in search_all_fkt(123.92578125, -25.48295117535531)]

    assert ['BR'] == [res['ISO2'] for res in search_all_fkt(-52.734375, -8.233237111274553)]
    assert ['PE'] == [res['ISO2'] for res in search_all_fkt(-72.24609375, -13.2399454992863)]
    assert ['AR'] == [res['ISO2'] for res in search_all_fkt(-66.97265625, -39.368279149160124)]

    assert search_fkt(0, 0) is None  # south atlantic ocean
    assert search_fkt(-37.6171875, 50.401515322782366) is None  # north atlantic ocean

    assert search_fkt(-107.75390625, -16.804541076383455) is None  # south atlantic ocean
    assert search_fkt(-143.7890625, 37.996162679728116) is None  # north atlantic ocean

    assert search_fkt(85.9765625, -13.923403897723334) is None  # indian ocean
    assert search_fkt(32.1240234375, 43.29320031385282) is None  # black see

    assert [] == list(search_all_fkt(0, 0))  # south atlantic ocean
    assert [] == list(search_all_fkt(-37.6171875, 50.401515322782366))  # north atlantic ocean

    assert [] == list(search_all_fkt(-107.75390625, -16.804541076383455))  # south atlantic ocean
    assert [] == list(search_all_fkt(-143.7890625, 37.996162679728116))  # north atlantic ocean

    assert [] == list(search_all_fkt(85.9765625, -13.923403897723334))  # indian ocean
    assert [] == list(search_all_fkt(32.1240234375, 43.29320031385282))  # black see


def test_invalid(collection):
    with pytest.raises(ValueError):
        GeoPIP(filename='xyz.json', geojson_dict=collection)

    with pytest.raises(ValueError):
        GeoPIP(filenam='xyz.json')

    with pytest.raises(ValueError):
        GeoPIP(geojson_dic=collection)

    with pytest.raises(ValueError):
        GeoPIP('xyz.json')

    with pytest.raises(ValueError):
        GeoPIP(geojson_dict=collection['features'])


def test_file_init(testdir, rand_lng, rand_lat):
    geo = GeoPIP(filename=testdir + '/sample.geo.json')

    assert testdir + '/sample.geo.json' in str(geo)

    _test_sample_geojson(geo, rand_lng, rand_lat)


def test_env_init(testdir, rand_lng, rand_lat):
    environ['REVERSE_GEOCODE_DATA'] = testdir + '/sample.geo.json'
    geo = GeoPIP()

    assert '<env = ' + testdir + '/sample.geo.json >' in str(geo)

    _test_sample_geojson(geo, rand_lng, rand_lat)


def test_dict_init(collection, rand_lng, rand_lat):
    geo = GeoPIP(geojson_dict=collection)

    assert '<dict>' in str(geo)

    _test_sample_geojson(geo, rand_lng, rand_lat)


def _test_sample_geojson(geo, rand_lng, rand_lat):
    assert len(geo.shapes) == 2  # star and trapezoid in '', rect and triangle in '800'
    assert sum(len(ps) for ps in geo.shapes.values()) == 4

    assert 2 == len(geo.shapes[''])
    assert 'star' == geo.shapes[''][0]['properties']['type']
    assert 'trapezoid' == geo.shapes[''][1]['properties']['type']

    assert 2 == len(geo.shapes['800'])
    assert 'rect' == geo.shapes['800'][0]['properties']['type']
    assert 'triangle' == geo.shapes['800'][1]['properties']['type']

    assert {'type': 'rect'} == geo.search(lng=0.5, lat=0.3)  # first in '800' (most precise)
    assert [{'type': 'rect'}, {'type': 'triangle'}, {'type': 'trapezoid'}] == list(geo.search_all(lng=0.5, lat=0.3))

    assert {'type': 'star'} == geo.search(lng=0., lat=0.)

    assert geo.search(lng=0.06866455078125, lat=0.0769042737833478) is None

    # out of range
    with pytest.raises(ValueError):
        geo.search(lng=182, lat=88)
    with pytest.raises(ValueError):
        geo.search(lng=178, lat=98)
    with pytest.raises(ValueError):
        geo.search(lng=-182, lat=-88)
    with pytest.raises(ValueError):
        geo.search(lng=-178, lat=-98)

    # nothing found
    for i_ in range(100):
        lng, lat = rand_lng(), rand_lat()
        if not (-2 <= lng <= 2 and -2 <= lat <= 2):
            assert geo.search(lng, lat) is None

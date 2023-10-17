# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals

from random import random

from geopip._geo_fkt import in_bbox
from geopip._pure import p_in_polygon, prepare

################################################################################
################                     prepare                    ################
################################################################################


def test_prepare_invalids(rect):
    ls = {"type": "LineString", "coordinates": rect}
    feature = {"geometry": ls, "properties": {"a": 1}, "type": "Feature"}

    assert [] == prepare(feature)

    mls = {"type": "MultiLineString", "coordinates": [rect]}
    feature = {"geometry": mls, "properties": {"a": 1}, "type": "Feature"}

    assert [] == prepare(feature)

    mp = {"type": "MultiPoint", "coordinates": rect}
    feature = {"geometry": mp, "properties": {"a": 1}, "type": "Feature"}

    assert [] == prepare(feature)


def test_prepare_polygon(rect):
    rect_poly = {"type": "Polygon", "coordinates": [rect]}
    rect_feature = {"geometry": rect_poly, "properties": {"a": 1}, "type": "Feature"}

    p_rect = prepare(rect_feature)

    assert 1 == len(p_rect)
    assert {"shape", "properties", "bounds"} == set(p_rect[0].keys())
    assert rect_poly == p_rect[0]["shape"]
    assert (0, 0, 1, 1) == p_rect[0]["bounds"]
    assert {"a": 1} == p_rect[0]["properties"]


def test_prepare_single_multypolygon(rect):
    rect_poly = {"type": "Polygon", "coordinates": [rect]}
    rect_mpoly = {"type": "MultiPolygon", "coordinates": [[rect]]}
    rect_feature = {"geometry": rect_mpoly, "properties": {"a": 1}, "type": "Feature"}

    p_rect = prepare(rect_feature)

    assert 1 == len(p_rect)
    assert {"shape", "properties", "bounds"} == set(p_rect[0].keys())
    assert rect_poly == p_rect[0]["shape"]
    assert (0, 0, 1, 1) == p_rect[0]["bounds"]
    assert {"a": 1} == p_rect[0]["properties"]


def test_prepare_many_multypolygon(rect, triangle, trapezoid):
    triangle_poly = {"type": "Polygon", "coordinates": [triangle]}
    rect_poly = {"type": "Polygon", "coordinates": [rect]}
    trapezoid_poly = {"type": "Polygon", "coordinates": [trapezoid]}
    mpoly = {"type": "MultiPolygon", "coordinates": [[triangle], [rect], [trapezoid]]}
    feature = {"geometry": mpoly, "properties": {"a": 1}, "type": "Feature"}

    prepared = prepare(feature)

    assert 3 == len(prepared)

    # triangle
    assert {"shape", "properties", "bounds"} == set(prepared[0].keys())
    assert triangle_poly == prepared[0]["shape"]
    assert (0, 0, 1, 1) == prepared[0]["bounds"]
    assert {"a": 1} == prepared[0]["properties"]

    # rect
    assert {"shape", "properties", "bounds"} == set(prepared[1].keys())
    assert rect_poly == prepared[1]["shape"]
    assert (0, 0, 1, 1) == prepared[1]["bounds"]
    assert {"a": 1} == prepared[1]["properties"]

    # trapezoid
    assert {"shape", "properties", "bounds"} == set(prepared[2].keys())
    assert trapezoid_poly == prepared[2]["shape"]
    assert (0, -1, 1, 1) == prepared[2]["bounds"]
    assert {"a": 1} == prepared[2]["properties"]


################################################################################
################                  p_in_polygon                  ################
################################################################################


def test_p_in_polygon_rect(rect, rand_lat, rand_lng):
    rect_cw = {"type": "Polygon", "coordinates": [list(reversed(rect))]}
    rect = {"type": "Polygon", "coordinates": [rect]}

    p_rect_cw = prepare({"geometry": rect_cw, "properties": {}})[0]
    p_rect = prepare({"geometry": rect, "properties": {}})[0]

    # inside
    for _i in range(100):
        p = (random(), random())
        assert p_in_polygon(p, p_rect)
        assert p_in_polygon(p, p_rect_cw)

    # outside
    for _i in range(100):
        p = (rand_lng(), rand_lat())
        if not (0 <= p[0] <= 1 and 0 <= p[1] <= 1):
            assert not p_in_polygon(p, p_rect)
            assert not p_in_polygon(p, p_rect_cw)


def test_p_in_polygon_rect_w_hole(rect):
    hole = [(0.5, 0.1), (0.2, 0.2), (0.75, 0.2), (0.5, 0.1)]  # cw
    rect_cw = {
        "type": "Polygon",
        "coordinates": [list(reversed(rect)), list(reversed(hole))],
    }
    rect = {"type": "Polygon", "coordinates": [rect, hole]}

    p_rect_cw = prepare({"geometry": rect_cw, "properties": {}})[0]
    p_rect = prepare({"geometry": rect, "properties": {}})[0]

    # in hole
    assert not p_in_polygon((0.5, 0.15), p_rect)
    assert not p_in_polygon((0.5, 0.15), p_rect_cw)

    # in poly, not in hole
    assert p_in_polygon((0.75, 0.3), p_rect)
    assert p_in_polygon((0.75, 0.3), p_rect_cw)


def test_p_in_polygon_star(star, rand_lat, rand_lng):
    star_cw = {"type": "Polygon", "coordinates": [list(reversed(star))]}
    star = {"type": "Polygon", "coordinates": [star]}

    p_star_cw = prepare({"geometry": star_cw, "properties": {}})[0]
    p_star = prepare({"geometry": star, "properties": {}})[0]

    # inside
    for _i in range(100):
        p = (random() * 0.0697 - 0.0257, random() * 0.0383 - 0.016)  # in center of star
        assert p_in_polygon(p, p_star)
        assert p_in_polygon(p, p_star_cw)

    # top star
    p = (0.006866455078125, 0.06454466408274376)
    assert p_in_polygon(p, p_star)
    assert p_in_polygon(p, p_star_cw)

    # bottom right
    p = (0.039825439453125, -0.034332273336096036)
    assert p_in_polygon(p, p_star)
    assert p_in_polygon(p, p_star_cw)

    # left
    p = (-0.0501251220703125, 0.008926391565455)
    assert p_in_polygon(p, p_star)
    assert p_in_polygon(p, p_star_cw)

    # outside
    box = p_star["bounds"]
    for _i in range(100):
        p = (rand_lng(), rand_lat())
        if not in_bbox(p, box):
            assert not p_in_polygon(p, p_star)
            assert not p_in_polygon(p, p_star_cw)
